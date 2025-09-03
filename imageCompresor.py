import streamlit as st
from PIL import Image
import pillow_heif
import io, zipfile, os, time, pandas as pd

logo = Image.open("Logo.png")

st.set_page_config(page_title="Bulk Image Compressor", page_icon=logo)
st.title("Image Compressor")
st.subheader("by Dafruz")
st.write("Upload beberapa gambar (JPG/PNG/HEIC) untuk dikompres")

# Daftarkan handler HEIF ke Pillow
pillow_heif.register_heif_opener()

# Upload banyak gambar
uploaded_files = st.file_uploader(
    "Pilih gambar",
    type=["jpg", "jpeg", "png", "heic", "heif"],
    accept_multiple_files=True
)

if uploaded_files:
    quality = st.slider("Pilih kualitas kompresi", 10, 95, 70)

    # Pilih format output
    output_format = st.selectbox(
        "Pilih format output",
        ["JPEG", "PNG", "WEBP"]
    )

    # Buat file ZIP di memory
    zip_buffer = io.BytesIO()
    file_data = []  # untuk menyimpan ukuran sebelum & sesudah

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for uploaded_file in uploaded_files:
            # Buka gambar (JPG/PNG/HEIC)
            image = Image.open(uploaded_file).convert("RGB")

            # Kompres
            img_io = io.BytesIO()
            save_params = {}

            # Atur parameter berdasarkan format
            if output_format == "JPEG":
                save_params = {"format": "JPEG", "quality": quality, "optimize": True}
                ext = ".jpg"
            elif output_format == "PNG":
                save_params = {"format": "PNG", "optimize": True}
                ext = ".png"
            elif output_format == "WEBP":
                save_params = {"format": "WEBP", "quality": quality}
                ext = ".webp"

            image.save(img_io, **save_params)
            img_io.seek(0)

            # Ukuran file
            original_size = uploaded_file.size / 1024  # KB
            compressed_size = len(img_io.getvalue()) / 1024  # KB
            reduction = ((original_size - compressed_size) / original_size * 100) if original_size > 0 else 0

            file_data.append({
                "Nama File": uploaded_file.name,
                "Ukuran Asli (KB)": f"{original_size:.2f}",
                "Ukuran Kompres (KB)": f"{compressed_size:.2f}",
                "Pengurangan (%)": f"{reduction:.1f}%"
            })

            # Tambahkan ke zip
            filename = os.path.splitext(uploaded_file.name)[0] + "_compressed" + ext
            zipf.writestr(filename, img_io.read())
    zip_buffer.seek(0)

    # Tampilkan tabel ringkasan
    st.dataframe(pd.DataFrame(file_data))

    # Tombol download
    st.download_button(
        label="⬇️ Download Semua (ZIP)",
        data=zip_buffer,
        file_name=f"compressed_images_{int(time.time())}.zip",
        mime="application/zip"
    )
