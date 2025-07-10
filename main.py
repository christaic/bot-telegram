import os
import io
from telegram import Update
from telegram.constants import MessageEntityType
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image as ExcelImage
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("7717678907:AAHiDoUQsn1tFueTH-RRows5HGZnpNI8Y50")

registro_estado = {}

def is_mentioning_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    entities = update.message.entities or []
    for entity in entities:
        if entity.type == MessageEntityType.MENTION:
            text = update.message.text[entity.offset:entity.offset + entity.length]
            if text.lower() == f"@{context.bot.username.lower()}":
                return True
    return False

def is_reply_to_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    return (
        update.message.reply_to_message and
        update.message.reply_to_message.from_user.id == context.bot.id
    )

def is_valid_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_type = update.message.chat.type
    if chat_type == "private":
        return True
    return is_mentioning_bot(update, context) or is_reply_to_bot(update, context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_valid_message(update, context):
        return
    group_id = update.effective_chat.id
    registro_estado[group_id] = {"step": 0, "data": {}}
    await update.message.reply_text("📍 Envíame el nombre de la calle y número de cuadra.")

async def reiniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.effective_chat.id
    registro_estado[group_id] = {"step": 0, "data": {}}
    await update.message.reply_text("🔄 Flujo reiniciado. Usa /start para comenzar de nuevo.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_valid_message(update, context):
        return
    group_id = update.effective_chat.id
    if group_id not in registro_estado:
        await update.message.reply_text("❗ Usa /start para comenzar el registro.")
        return
    step = registro_estado[group_id]["step"]
    if step == 0:
        registro_estado[group_id]["data"]["calle"] = update.message.text
        registro_estado[group_id]["step"] = 1
        await update.message.reply_text("🖼️ Envíame la foto del ANTES.")
    else:
        await update.message.reply_text("Sigue el flujo.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_valid_message(update, context):
        return
    group_id = update.effective_chat.id
    if group_id not in registro_estado:
        await update.message.reply_text("❗ Usa /start para comenzar el registro.")
        return
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    image = Image.open(io.BytesIO(photo_bytes))
    image_path = f"temp_{group_id}_{registro_estado[group_id]['step']}.jpg"
    image.save(image_path)
    step = registro_estado[group_id]["step"]
    if step == 1:
        registro_estado[group_id]["data"]["foto_antes"] = image_path
        registro_estado[group_id]["step"] = 2
        await update.message.reply_text("🖼️ Envíame la foto del DESPUÉS.")
    elif step == 2:
        registro_estado[group_id]["data"]["foto_despues"] = image_path
        registro_estado[group_id]["step"] = 3
        await update.message.reply_text("🏷️ Envíame la foto de la ETIQUETA.")
    elif step == 3:
        registro_estado[group_id]["data"]["foto_etiqueta"] = image_path
        registro_estado[group_id]["step"] = 4
        await update.message.reply_text("📌 Envíame tu ubicación GPS.")
    else:
        await update.message.reply_text("Ya recibí las fotos. Envíame la ubicación.")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_valid_message(update, context):
        return
    group_id = update.effective_chat.id
    if group_id not in registro_estado:
        await update.message.reply_text("❗ Usa /start para comenzar el registro.")
        return
    data = registro_estado[group_id]["data"]
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    data["lat"] = lat
    data["lon"] = lon

    filename = f"grupo_{group_id}.xlsx"
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Calle y cuadra", "Latitud", "Longitud", "Foto Antes", "Foto Después", "Foto Etiqueta"])
        for col in ['D', 'E', 'F']:
            ws.column_dimensions[col].width = 20

    ws.append([data["calle"], lat, lon, "", "", ""])
    row = ws.max_row
    for i, key in enumerate(["foto_antes", "foto_despues", "foto_etiqueta"]):
        img = ExcelImage(data[key])
        img.width, img.height = 120, 120
        col = chr(68 + i)
        ws.add_image(img, f"{col}{row}")
    ws.row_dimensions[row].height = 90
    wb.save(filename)
    registro_estado[group_id] = {"step": 0, "data": {}}
    await update.message.reply_text("✅ Registro guardado. Usa /start para otro o /exportar para descargar Excel.")

async def exportar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_valid_message(update, context):
        return
    group_id = update.effective_chat.id
    filename = f"grupo_{group_id}.xlsx"
    if os.path.exists(filename):
        await update.message.reply_document(open(filename, "rb"))
    else:
        await update.message.reply_text("❌ No se encontró archivo para este grupo.")

# Construcción y registro de comandos
app = ApplicationBuilder().token("7717678907:AAHiDoUQsn1tFueTH-RRows5HGZnpNI8Y50").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reiniciar", reiniciar))
app.add_handler(CommandHandler("exportar", exportar))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.LOCATION, handle_location))
app.run_polling()
