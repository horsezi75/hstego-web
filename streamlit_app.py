
import io
import struct
import streamlit as st
from PIL import Image

st.set_page_config(page_title="LSB 图片隐写演示", page_icon="🔐")
st.title("🔐 LSB 图片隐写演示")
st.write("将文字隐藏到 PNG 图片中，再从图片中提取文字。")
st.warning("这是 LSB 教学演示版，不是官方 HStego 算法。")

MAGIC = b"LSB1"

def embed(img, message):
    img = img.convert("RGB")
    payload = MAGIC + message.encode("utf-8")
    data = struct.pack(">I", len(payload)) + payload
    bits = [(b >> i) & 1 for b in data for i in range(7, -1, -1)]
    pixels = list(img.getdata())

    if len(bits) > len(pixels) * 3:
        raise ValueError("文字太长，请换一张更大的图片或缩短文字。")

    result = []
    index = 0
    for pixel in pixels:
        channels = list(pixel)
        for i in range(3):
            if index < len(bits):
                channels[i] = (channels[i] & 254) | bits[index]
                index += 1
        result.append(tuple(channels))

    out = Image.new("RGB", img.size)
    out.putdata(result)
    return out

def extract(img):
    pixels = list(img.convert("RGB").getdata())
    bits = [channel & 1 for pixel in pixels for channel in pixel]

    if len(bits) < 32:
        raise ValueError("图片太小。")

    length = 0
    for bit in bits[:32]:
        length = (length << 1) | bit

    if length < 4 or length > (len(bits) - 32) // 8:
        raise ValueError("没有找到有效信息，请上传本网页生成的 PNG。")

    data = bytearray()
    for start in range(32, 32 + length * 8, 8):
        value = 0
        for bit in bits[start:start + 8]:
            value = (value << 1) | bit
        data.append(value)

    if not data.startswith(MAGIC):
        raise ValueError("这不是本网页生成的隐写图片。")

    return data[4:].decode("utf-8")

hide_tab, extract_tab = st.tabs(["🔒 隐藏文字", "🔓 提取文字"])

with hide_tab:
    cover = st.file_uploader("上传原始图片", type=["png", "jpg", "jpeg", "bmp"])
    message = st.text_area("输入要隐藏的文字")

    if st.button("生成隐写图片"):
        if cover is None or not message:
            st.error("请上传图片并输入文字。")
        else:
            try:
                with Image.open(cover) as source:
                    result = embed(source, message)
                buffer = io.BytesIO()
                result.save(buffer, format="PNG")
                data = buffer.getvalue()
                st.image(data, caption="生成的隐写图片")
                st.download_button(
                    "下载隐写图片",
                    data=data,
                    file_name="lsb_stego.png",
                    mime="image/png"
                )
                st.success("生成成功！")
            except Exception as e:
                st.error(f"生成失败：{e}")

with extract_tab:
    stego = st.file_uploader("上传隐写 PNG", type=["png"])

    if st.button("提取秘密文字"):
        if stego is None:
            st.error("请先上传隐写图片。")
        else:
            try:
                with Image.open(stego) as source:
                    secret = extract(source)
                st.success("提取成功！")
                st.text_area("提取到的文字", value=secret)
            except Exception as e:
                st.error(f"提取失败：{e}")

st.caption("课程实验：LSB 图像隐写原理演示")
