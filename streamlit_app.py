import streamlit as st
from PIL import Image
import io
import struct

st.set_page_config(
    page_title="HStego Web",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 HStego Web")
st.caption("图像隐写与秘密信息提取 · Web Demo")

st.info(
    "当前版本先实现 PNG 图片隐写演示。"
    "此处使用的是简单的 LSB 原型算法，并非 HStego 官方算法；"
    "后续需要接入官方库才能完成基于 HStego 的版本。"
)

tab1, tab2 = st.tabs(["📩 嵌入秘密信息", "🔎 提取秘密信息"])

def embed_demo(image, message):
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")
    else:
        image = image.copy()

    pixels = list(image.getdata())
    raw = message.encode("utf-8")
    payload = struct.pack(">I", len(raw)) + raw
    bits = ''.join(f'{byte:08b}' for byte in payload)

    if len(bits) > len(pixels) * 3:
        raise ValueError("秘密信息太长，请换用更大的图片或缩短文字。")

    new_pixels = []
    index = 0
    for pixel in pixels:
        channels = list(pixel)
        for c in range(3):
            if index < len(bits):
                channels[c] = (channels[c] & 254) | int(bits[index])
                index += 1
        new_pixels.append(tuple(channels))

    result = Image.new(image.mode, image.size)
    result.putdata(new_pixels)
    return result

def extract_demo(image):
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    bits = []
    for pixel in image.getdata():
        for channel in pixel[:3]:
            bits.append(str(channel & 1))

    if len(bits) < 32:
        raise ValueError("图片数据不足。")

    length = int(''.join(bits[:32]), 2)
    if length > (len(bits) - 32) // 8:
        raise ValueError("没有找到有效的演示数据，或图片不是本工具生成的。")

    data_bits = bits[32:32 + length * 8]
    raw = bytes(
        int(''.join(data_bits[i:i + 8]), 2)
        for i in range(0, len(data_bits), 8)
    )
    return raw.decode("utf-8")

with tab1:
    st.subheader("把文字嵌入图片")
    cover_file = st.file_uploader(
        "上传原始图片（建议 PNG）",
        type=["png", "bmp"],
        key="cover"
    )
    secret = st.text_area("秘密文字", placeholder="输入要隐藏的内容……")
    password = st.text_input(
        "密码（当前演示算法暂未使用密码加密）",
        type="password",
        key="embed_password"
    )

    if cover_file:
        cover = Image.open(cover_file)
        st.image(cover, caption="原始图片", use_container_width=True)

        if st.button("🔐 生成隐写图片", type="primary"):
            if not secret:
                st.warning("请先输入秘密文字。")
            else:
                try:
                    result = embed_demo(cover, secret)
                    output = io.BytesIO()
                    result.save(output, format="PNG")
                    st.success("演示隐写图片生成成功！")
                    st.image(result, caption="生成的 PNG 图片", use_container_width=True)
                    st.download_button(
                        "⬇️ 下载隐写图片",
                        data=output.getvalue(),
                        file_name="hstego_demo.png",
                        mime="image/png"
                    )
                except Exception as e:
                    st.error(str(e))

with tab2:
    st.subheader("从图片中提取文字")
    stego_file = st.file_uploader(
        "上传本工具生成的演示图片",
        type=["png", "bmp"],
        key="stego"
    )
    if stego_file:
        st.image(stego_file, caption="待提取图片", use_container_width=True)
        if st.button("🔎 提取秘密文字", type="primary"):
            try:
                hidden = extract_demo(Image.open(stego_file))
                st.success("提取完成")
                st.text_area("提取到的秘密文字", value=hidden, height=150)
            except Exception as e:
                st.error(str(e))

st.divider()
st.caption("课程项目原型 · 后续版本将接入 HStego 官方算法并补充密码处理。")
