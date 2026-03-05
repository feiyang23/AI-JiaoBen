# app/utils/common_util.py
import hashlib

# 密码加密
def encrypt_password(password: str) -> str:
    md5 = hashlib.md5()
    md5.update(password.encode("utf-8"))
    return md5.hexdigest()

# 密码校验
def check_password(plain_pwd: str, encrypt_pwd: str) -> bool:
    return encrypt_password(plain_pwd) == encrypt_pwd