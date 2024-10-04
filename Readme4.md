Here's the `README.md` file based on today's lesson on Telegram bot development with a focus on buttons and keyboards:

---

# Telegram Bot - Button and Keyboard Implementation

### **Lesson Plan:**

Today we will explore the interface of Telegram bots and implement buttons and menus. The lesson will cover:
1. Types of buttons in Telegram bots.
2. Creating and adding buttons to a bot.

---

## **1. Reply Keyboard**

A **Reply keyboard** replaces the default keyboard with custom buttons. These buttons send commands to the bot when pressed, similar to typing a command like `/help` or `/start`.

### **Creating Reply Buttons:**

To create reply buttons, follow these steps:

1. **Import necessary libraries:**
   ```python
   from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
   ```

2. **Define the keyboard layout:**
   ```python
   main = ReplyKeyboardMarkup(keyboard=[
      [KeyboardButton(text="Test Button 1")],
      [KeyboardButton(text="Test Button 2"), KeyboardButton(text="Test Button 3")]
   ], resize_keyboard=True)
   ```

3. **Connect the keyboard to the bot in `main.py`:**
   ```python
   import keyboards as kb

   @dp.message(CommandStart())
   async def start(message: Message):
      await message.answer(f'Hello, {message.from_user.first_name}', reply_markup=kb.main)
   ```

The `resize_keyboard=True` parameter resizes the buttons for better appearance.

### **Handling Reply Button Clicks:**

1. Create a message handler for the buttons:
   ```python
   @dp.message(F.text == "Test Button 1")
   async def test_button(message: Message):
      await message.answer('Reply button clicked!')
   ```

---

## **2. Inline Keyboard and Builder**

An **Inline keyboard** is attached to a specific message, and clicking a button triggers a server request, not a text message.

### **Creating Inline Buttons:**

1. **Import additional libraries for inline buttons:**
   ```python
   from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
   ```

2. **Define the inline keyboard:**
   ```python
   inline_keyboard_test = InlineKeyboardMarkup(inline_keyboard=[
      [InlineKeyboardButton(text="Video", url='https://www.youtube.com/watch?v=HfaIcB4Ogxk')]
   ])
   ```

3. **Attach the inline keyboard to a message:**
   ```python
   @dp.message(CommandStart())
   async def start(message: Message):
      await message.answer(f'Hello, {message.from_user.first_name}', reply_markup=kb.inline_keyboard_test)
   ```

### **Handling Inline Button Actions (Callback):**

1. **Define the callback handler:**
   ```python
   @dp.callback_query(F.data == 'news')
   async def news(callback: CallbackQuery):
      await callback.answer("Loading news...")
      await callback.message.answer('Here are the latest news!')
   ```

---

## **3. Keyboard Builder**

The **Keyboard Builder** is useful when the button list is dynamic (e.g., coming from a database). It automatically creates buttons from a list.

### **Creating a Builder:**

1. **Import the builder library:**
   ```python
   from aiogram.utils.keyboard import InlineKeyboardBuilder
   ```

2. **Define a list of dynamic buttons:**
   ```python
   test = ["Button 1", "Button 2", "Button 3", "Button 4"]
   ```

3. **Create an async function to generate the keyboard:**
   ```python
   async def test_keyboard():
      keyboard = InlineKeyboardBuilder()
      for key in test:
         keyboard.add(InlineKeyboardButton(text=key, url='https://www.youtube.com'))
      return keyboard.adjust(2).as_markup()
   ```

4. **Attach the keyboard to a message in `main.py`:**
   ```python
   @dp.callback_query(F.data == 'news')
   async def news(callback: CallbackQuery):
      await callback.message.edit_text('Updated news!', reply_markup=await kb.test_keyboard())
   ```

---

## **Key Differences:**

- **Reply Keyboard**:
  - Appears at the bottom of the chat.
  - Sends predefined text as a command.
  - Cannot include URLs or other interactive elements.

- **Inline Keyboard**:
  - Attached to a specific message.
  - Sends a request (callback) to the server without sending a message.
  - Can include URLs and trigger various server actions.

---

### **Lesson Summary:**

- Explored different types of buttons in Telegram bots.
- Created both **Reply** and **Inline** keyboards.
- Handled button clicks with callbacks and replies.
