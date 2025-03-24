import streamlit as st
from PIL import Image
import numpy as np
import csv
import os
import qrcode
import io
import cv2


st.set_page_config(page_title="qkd talk", page_icon="🤓", layout="wide")
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #ff9a9e, #fad0c4);
        color: white;
        font-family: monospace, monospace;
    }
    .stButton > button {
        background: linear-gradient(to right, #ff758c, #ff7eb3);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background: linear-gradient(to right, #ff416c, #ff4b7d);
    }
    .stTextInput > div > input {
        background: linear-gradient(to right, #a8e6cf, #dcedc1);
        color: black;
        border: 1px solid black;
        padding: 10px;
        border-radius: 5px;
    }
    .stSidebar {
        background: linear-gradient(to bottom, #ff9a9e, #fad0c4) !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


def create_credentials_file():
    with open("user_credentials.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password"])


def register_user(username, password):
    with open("user_credentials.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, password])
    st.success("Registration successful. Please log in.")

def login_user(username, password):
    with open("user_credentials.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! You are now logged in.")
                return True
    st.error("Invalid username or password. Please try again.")
    return False

def bb84_key_exchange(length):
    alice_bits = np.random.randint(2, size=length)
    alice_bases = np.random.randint(2, size=length)
    bob_bases = np.random.randint(2, size=length)
    bob_results = [alice_bits[i] if alice_bases[i] == bob_bases[i] else np.random.randint(2) for i in range(length)]
    return alice_bits, alice_bases, bob_bases, bob_results


def encrypt_message(message, key):
    encrypted_message = ''.join(chr(ord(message[i]) ^ key[i % len(key)]) for i in range(len(message)))
    return encrypted_message


def decrypt_message(encrypted_message, key):
    decrypted_message = ''.join(chr(ord(encrypted_message[i]) ^ key[i % len(key)]) for i in range(len(encrypted_message)))
    return decrypted_message


def encrypt_image(image, key):
    _, buffer = cv2.imencode('.png', image)
    image_data = buffer.tobytes()
    encrypted_image_data = bytearray()
    for i in range(len(image_data)):
        encrypted_byte = image_data[i] ^ key[i % len(key)]  # XOR operation with the key
        encrypted_image_data.append(encrypted_byte)
    return bytes(encrypted_image_data)


def decrypt_image(encrypted_image_data, key):
    decrypted_image_data = bytearray()
    for i in range(len(encrypted_image_data)):
        decrypted_byte = encrypted_image_data[i] ^ key[i % len(key)]  # XOR operation with the key
        decrypted_image_data.append(decrypted_byte)
    decrypted_image = cv2.imdecode(np.frombuffer(bytes(decrypted_image_data), np.uint8), 1)
    return decrypted_image


def generate_qkd_key_pair(image_shape):
    key_length = image_shape[0] * image_shape[1] * 3  # Assuming RGB images
    sender_key = np.random.randint(256, size=key_length, dtype=np.uint8)
    receiver_key = np.random.randint(256, size=key_length, dtype=np.uint8)
    return sender_key, receiver_key


def encrypt_image_qkd(image_data, qkd_key):
    encrypted_image_data = bytearray()
    for i in range(len(image_data)):
        encrypted_byte = image_data[i] ^ qkd_key[i % len(qkd_key)]  # XOR operation with QKD key
        encrypted_image_data.append(encrypted_byte)
    return bytes(encrypted_image_data)


def decrypt_image_qkd(encrypted_image_data, qkd_key, image_shape):
    decrypted_image_data = bytearray()
    for i in range(len(encrypted_image_data)):
        decrypted_byte = encrypted_image_data[i] ^ qkd_key[i % len(qkd_key)]  # XOR operation with QKD key
        decrypted_image_data.append(decrypted_byte)
    return np.array(decrypted_image_data).reshape(image_shape)


def generate_qr_code(shared_key):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=2,
    )
    qr.add_data(shared_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="green", back_color="white")
    return img


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("QKD chat")
        st.subheader("Modified BB84 based texting application!")
        st.sidebar.title("Hey there, nice to meet ya.")

        option = st.sidebar.radio("Have I seen you before?", ("Login", "Register"))
        if option == "Register":
            new_username = st.sidebar.text_input("Enter New Username")
            new_password = st.sidebar.text_input("Enter New Password", type="password")
            if st.sidebar.button("Register"):
                register_user(new_username, new_password)
        elif option == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                login_user(username, password)

    elif st.sidebar.button("Logout"):
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        navigation_option = st.sidebar.radio("Go to:", ["Secure Chat Interface"])


        if navigation_option == "Secure Chat Interface":
            st.subheader("Secure Chat Interface")
            st.write(f"Welcome to the Secure Chat Interface, {st.session_state.username}!")

            message_to_send = st.text_area("Type your message here to send:")
            if st.button("Send Message"):
                st.success("Message sent successfully!")
                shared_key = bb84_key_exchange(len(message_to_send))[0]
                encrypted_message = encrypt_message(message_to_send, shared_key)

                qr_code_img = generate_qr_code(''.join(map(str, shared_key)))
                img_byte_arr = io.BytesIO()
                qr_code_img.save(img_byte_arr, format='PNG')
                st.image(img_byte_arr, caption="QR Code for Shared Key", use_column_width=False, width=250)

                st.session_state.message_sent = message_to_send
                st.session_state.shared_key = shared_key
                st.session_state.encrypted_message = encrypted_message
                st.session_state.encrypted_message_sent = True

            if "encrypted_message_sent" in st.session_state and st.session_state.encrypted_message_sent:
                st.write("Encrypted Message:", st.session_state.encrypted_message)
                st.write("Shared Key:", ''.join(map(str, st.session_state.shared_key)))

            encrypted_message_received = st.text_input("Enter the encrypted message received:")
            shared_key_received = st.text_input("Enter the shared key received:")
            if st.button("Decrypt Message"):
                encrypted_message_received = encrypted_message_received.strip()
                if encrypted_message_received:
                    decrypted_message = decrypt_message(encrypted_message_received, list(map(int, shared_key_received)))
                    st.write("Decrypted message:", decrypted_message)
                    st.success("Message decrypted successfully!")
                else:
                    st.error("Please enter a valid encrypted message.")

if __name__ == "__main__":
    main()