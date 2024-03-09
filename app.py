import streamlit as st
import requests
from google.cloud import speech, texttospeech
import struct
import os
import cv2
import time
import base64
import google.generativeai as genai

# Function to get Gemini response
def get_gemini_response(cv_text, job_description, prompt, google_api_key):
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([cv_text, job_description, prompt])
    return response.text

# Function to record audio
def record_audio(stream, rate, frame_length, record_seconds):
    print("Recording...")
    frames = []
    for _ in range(0, int(rate / frame_length * record_seconds)):
        try:
            data = stream.read(frame_length, exception_on_overflow=False) 
            frames.append(data)
        except IOError as e:
            if e.errno == pyaudio.paInputOverflowed:
                continue  # Proceed to the next frame
    print("Recording stopped.")
    return b''.join(frames)

# Function to transcribe audio
def transcribe_audio(client, audio_data):
    audio = speech.RecognitionAudio(content=audio_data)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    if response.results:
        for result in response.results:
            print("Transcribed text: {}".format(result.alternatives[0].transcript))
        return response.results[0].alternatives[0].transcript
    else:
        print("No transcription results.")
        return None

# Function for Google Text-to-Speech
def text_to_speech_google(text, client):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

# Main function for Streamlit app
def main():
    st.title("Gemni Pro Interview Bot")

    # Input fields for user
    cv_text = st.text_area("Paste Your CV/Resume here", height=200)
    job_description = st.text_area("Job Description", height=200)
    prompt = st.text_area("Prompt", height=200)
    google_api_key = st.text_input("Google API Key", type="password")

    if st.button("Start Interview"):
        if not cv_text or not job_description or not prompt or not google_api_key:
            st.warning("Please fill out all fields.")
        else:
            st.info("Generating interview questions...")
            gemini_response = get_gemini_response(cv_text, job_description, prompt, google_api_key)

            if gemini_response:
                st.success("Questions generated successfully!")
                st.write("Here are the interview questions:")
                for question in gemini_response:
                    st.write(f"- {question}")
            else:
                st.error("Failed to generate questions.")

if __name__ == "__main__":
    main()
