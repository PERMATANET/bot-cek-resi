import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Log aktivitas bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# MASUKKAN TOKEN ANDA DI SINI
TELEGRAM_TOKEN = "8658460686:AAGIYGq_M-XB9cXj-godld9Xd-zdO3M_Ob8"
API_KEY_RESI = "sk_ymql5tdaqb57ib4oexy625rashtvd3czwt4j31c1ukhopggix3sjgtfru0kgznen"

# Fungsi saat user mengetik /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Membuat daftar pilihan kurir (Inline Keyboard) seperti di gambar
    keyboard = [
        [InlineKeyboardButton("JNE", callback_data='jne'), InlineKeyboardButton("J&T Express", callback_data='jnt'), InlineKeyboardButton("SiCepat", callback_data='sicepat')],
        [InlineKeyboardButton("Anteraja", callback_data='anteraja'), InlineKeyboardButton("POS Indonesia", callback_data='pos'), InlineKeyboardButton("TIKI", callback_data='tiki')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 **Akses Diterima!**\n\nSilakan pilih kurir terlebih dahulu:", 
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Fungsi saat user memilih kurir
async def pilih_kurir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Menyimpan pilihan kurir ke dalam data sesi user
    context.user_data['kurir_terpilih'] = query.data
    
    await query.message.reply_text(
        f"✅ **Kurir dipilih: {query.data.upper()}**\n\n"
        "Silakan **kirim satu atau banyak nomor resi sekaligus** (pisahkan dengan baris baru/enter).",
        parse_mode="Markdown"
    )

# Fungsi untuk memproses nomor resi dan memanggil API Cek Resi
async def proses_resi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kurir = context.user_data.get('kurir_terpilih')
    
    # Jika user belum memilih kurir
    if not kurir:
        await update.message.reply_text("❌ Silakan pilih kurir terlebih dahulu dengan mengetik /start")
        return
        
    # Mengambil nomor resi dari pesan teks user
    nomor_resi = update.message.text.strip()
    
    # Contoh pemanggilan API (Disesuaikan dengan struktur API pihak ketiga yang Anda gunakan)
    # Di sini kita menggunakan contoh struktur umum API Cek Resi
    url_api = f"https://binderbyte.com{API_KEY_RESI}&courier={kurir}&awb={nomor_resi}"
    
    await update.message.reply_text("🔍 Sedang mengecek resi, mohon tunggu...")
    
    try:
        response = requests.get(url_api).json()
        
        if response.get('status') == 200:
            data = response['data']
            summary = data['summary']
            history = data['history'][0] # Mengambil riwayat terakhir
            
            # Menyusun format pesan agar mirip dengan contoh gambar Anda
            pesan_detail = (
                "📦 **DETAIL PENGIRIMAN**\n"
                "-----------------------------------------\n"
                f"**Status:** {summary['status'].upper()}\n"
                f"**No. Resi:** {summary['awb']}\n"
                f"**Courier:** {summary['courier']}\n"
                f"**Pengirim:** {data['detail']['shipper']}\n"
                f"**Asal:** {data['detail']['origin']}\n"
                f"**Penerima:** {data['detail']['receiver']}\n"
                f"**Tujuan:** {data['detail']['destination']}\n"
                "-----------------------------------------\n"
                "📌 **RIWAYAT TERAKHIR:**\n"
                f"⏱ {history['date']}\n"
                f"💬 {history['desc']}\n"
            )
            await update.message.reply_text(pesan_detail, parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Nomor resi tidak ditemukan atau kurir tidak sesuai.")
            
    except Exception as e:
        await update.message.reply_text("⚠️ Terjadi kesalahan saat menghubungi server kurir.")

def main():
    # Menjalankan aplikasi bot
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(pilih_kurir))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, proses_resi))
    
    print("Bot sedang berjalan...")
    app.run_polling()

if __name__ == '__main__':
    main()
