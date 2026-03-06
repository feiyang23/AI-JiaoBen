# app/utils/xfyun_lfasr_util.py
import json
import logging
import time
import os
from typing import Optional, Tuple
from xfyunsdkspeech.lfasr_client import LFasrClient
from xfyunsdkcore.model.lfasr_model import UploadParam
from app.core.settings import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xfyun_lfasr")

class XFYunLFasrUtil:
    """讯飞LFasr语音转写工具类"""
    def __init__(self):
        # 初始化讯飞客户端
        self.client = LFasrClient(
            app_id=settings.XF_APP_ID,
            secret_key=settings.XF_API_SECRET
        )
        self.max_timeout = settings.XF_AUDIO_TIMEOUT  # 最大等待时间（秒）
        self.poll_interval = settings.XF_AUDIO_INTERVAL  # 轮询间隔（秒）

    def transcribe_audio(self, audio_bytes: bytes, filename: str) -> Tuple[Optional[str], str]:
        """
        音频二进制转写为文本
        :param audio_bytes: 音频二进制数据
        :param filename: 音频文件名（用于识别格式/讯飞上传）
        :return: (转写文本, 状态信息)
        """
        try:
            # 1. 临时保存音频二进制到本地（讯飞SDK要求传入文件路径，而非直接传二进制）
            temp_dir = "temp_audio"
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, filename)
            
            # 写入临时文件
            with open(temp_file_path, "wb") as f:
                f.write(audio_bytes)
            
            # 2. 构造上传参数
            file_size = os.path.getsize(temp_file_path)
            upload_param = UploadParam(
                audioMode="fileStream",
                fileName=filename,
                fileSize=file_size
            )
            
            # 3. 上传音频文件到讯飞
            logger.info(f"开始上传音频文件：{filename}（大小：{file_size}字节）")
            upload_resp = self.client.upload(upload_param.to_dict(), temp_file_path)
            upload_data = json.loads(upload_resp)
            
            # 校验上传结果
            if upload_data["code"] != "000000":
                error_msg = f"音频上传失败：{upload_data}"
                logger.error(error_msg)
                return None, error_msg
            
            order_id = upload_data["content"]["orderId"]
            logger.info(f"音频上传成功，订单ID：{order_id}")
            
            # 4. 轮询查询转写结果
            status = 3  # 3=处理中
            elapsed_time = 0  # 已等待时间
            trans_text = None
            
            while status == 3 and elapsed_time < self.max_timeout:
                # 构造查询参数
                query_param = {"orderId": order_id}
                result_resp = self.client.get_result(query_param)
                result_data = json.loads(result_resp)
                
                # 校验查询结果
                if result_data["code"] != "000000":
                    error_msg = f"查询转写结果失败：{result_data}"
                    logger.error(error_msg)
                    return None, error_msg
                
                # 解析状态
                status = result_data['content']['orderInfo']['status']
                if status == 0:
                    logger.info(f"订单{order_id}已创建，等待处理...")
                elif status == 3:
                    logger.info(f"订单{order_id}处理中（已等待{elapsed_time}秒）...")
                elif status == 4:
                    # 转写完成，解析文本
                    order_result = result_data['content']['orderResult']
                    order_data = json.loads(order_result)
                    trans_text = order_data.get("lattice", "")
                    # 提取纯文本（过滤讯飞返回的格式信息）
                    if trans_text:
                        trans_text = self._extract_pure_text(trans_text)
                    logger.info(f"订单{order_id}转写完成，文本长度：{len(trans_text) if trans_text else 0}")
                    return trans_text, "转写成功"
                elif status == -1:
                    fail_type = result_data['content']['orderInfo']['failType']
                    error_msg = f"订单{order_id}转写失败，失败类型：{fail_type}"
                    logger.error(error_msg)
                    return None, error_msg
                
                # 等待后继续轮询
                time.sleep(self.poll_interval)
                elapsed_time += self.poll_interval
            
            # 超时处理
            if elapsed_time >= self.max_timeout:
                error_msg = f"订单{order_id}转写超时（超过{self.max_timeout}秒）"
                logger.error(error_msg)
                return None, error_msg
            
            return None, f"转写状态异常：{status}"
        
        except Exception as e:
            error_msg = f"转写过程异常：{str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg
        
        finally:
            # 清理临时文件（关键：避免磁盘占用）
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    @staticmethod
    def _extract_pure_text(lattice_str: str) -> str:
        """
        提取讯飞返回结果中的纯文本（过滤格式标签）
        :param lattice_str: 讯飞返回的lattice字段
        :return: 纯转写文本
        """
        try:
            # 解析lattice JSON（讯飞返回的是JSON字符串）
            lattice_data = json.loads(lattice_str)
            pure_text = ""
            # 遍历每一句转写结果
            for sentence in lattice_data.get("st", {}).get("rt", []):
                pure_text += sentence.get("ws", [])[0].get("cw", [])[0].get("w", "")
            return pure_text.strip()
        except Exception as e:
            logger.error(f"提取纯文本失败：{str(e)}")
            return lattice_str  # 解析失败则返回原始内容