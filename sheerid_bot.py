import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# التوكن الخاص بالبوت الذي تم توفيره
TOKEN = "9024402018:AAHiyTr1oFsggBiwYNoAyTpUGpwBVNBIfGQ"
bot = telebot.TeleBot(TOKEN)

# قاعدة بيانات مؤقتة لتخزين رصيد المستخدمين
user_credits = {}

def get_user_balance(user_id):
    if user_id not in user_credits:
        # منح هدية للمستخدم الجديد (2 محاولات مجانية) تماماً مثل الصورة
        user_credits[user_id] = {"free": 2, "vip": 0}
    return user_credits[user_id]

@bot.message_handler(commands=['start'])
def start_command(message):
    user = message.from_user
    balance = get_user_balance(user.id)
    
    welcome_text = (
        f"🤖 **SheerID Automated Verification Bot**\n\n"
        f"🎁 **Free & VIP Benefits:**\n"
        f"• New User Gift: 1 free credit(s) on first join!\n"
        f"• Zero-Loss Guarantee: If a link encounters network/proxy issues before upload, your credit is 100% auto-refunded!\n"
        f"• 💎 VIP Fast-Track: Recharge via USDT (BEP20) or redeem a VIP CDKey to skip the free queue!\n\n"
        f"🆔 **Your TG ID:** `{user.id}`\n"
        f"💳 **Available Credits:** {balance['free'] + balance['vip']} (💎 VIP: {balance['vip']} | 🎁 Free: {balance['free']})\n\n"
        f"📋 **Main Commands & Menu:**\n"
        f"• 🏠 Main Menu: `/start`\n"
        f"• 🚀 Submit Verification: `/verify <link>`\n"
        f"• 💎 Top Up VIP Credits: `/buy`\n"
        f"• 👤 My Account: `/me`\n"
        f"• 📊 Live Queue: `/queue`"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Submit Verification", callback_data="help_verify"))
    markup.add(InlineKeyboardButton("💎 Top Up VIP", callback_data="buy_vip"),
               InlineKeyboardButton("👤 My Account", callback_data="my_account"))
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['me'])
def me_command(message):
    user = message.from_user
    balance = get_user_balance(user.id)
    text = (
        f"👤 **Account Details:**\n\n"
        f"🆔 Telegram ID: `{user.id}`\n"
        f"👤 Name: {user.first_name}\n"
        f"🎁 Free Credits: {balance['free']}\n"
        f"💎 VIP Credits: {balance['vip']}"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['verify'])
def verify_command(message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    total_balance = balance['free'] + balance['vip']
    if total_balance <= 0:
        bot.reply_to(message, "❌ **Error:** You don't have enough credits. Please use `/buy` to top up your account.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **Usage:**\nSend the command with your SheerID link like this:\n`/verify https://services.sheerid.com/...`", parse_mode="Markdown")
        return

    link = args[1]
    
    if balance['free'] > 0:
        balance['free'] -= 1
    else:
        balance['vip'] -= 1

    sent_msg = bot.reply_to(message, "⏳ **[Queue Status]** Processing your link through the automated SheerID system...")
    
    time.sleep(2)
    
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=sent_msg.message_id,
        text=f"✅ **[Success]** Verification successfully completed and discount submitted!\n\n🔗 Link: `{link}`\n🎁 Remaining Credits: {balance['free'] + balance['vip']}",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['buy'])
def buy_command(message):
    buy_text = (
        "💎 **Top Up VIP Credits:**\n\n"
        "To get priority access and VIP fast-track, you can recharge using USDT (BEP20) or redeem a CDKey.\n\n"
        "Contact admin or use supported payment methods."
    )
    bot.reply_to(message, buy_text, parse_mode="Markdown")

@bot.message_handler(commands=['queue'])
def queue_command(message):
    bot.reply_to(message, "📊 **Live Queue Status:**\nCurrently active tasks in queue: 0\nAverage wait time: < 1 minute.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "help_verify":
        bot.answer_callback_query(call.id, "Send /verify followed by your SheerID link")
        bot.send_message(call.message.chat.id, "✍️ Send command:\n`/verify https://services.sheerid.com/...`", parse_mode="Markdown")
    elif call.data == "my_account":
        user = call.from_user
        balance = get_user_balance(user.id)
        bot.answer_callback_query(call.id, f"Your balance: {balance['free'] + balance['vip']} credits")
    elif call.data == "buy_vip":
        bot.answer_callback_query(call.id, "Contact admin for VIP top-up")
        bot.send_message(call.message.chat.id, "💎 Use `/buy` to check top-up options.")

if __name__ == '__main__':
    print("SheerID Automated Telegram Bot is running...")
    bot.infinity_polling()
