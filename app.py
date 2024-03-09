import streamlit as st
from google.cloud import speech, texttospeech
import sounddevice as sd
import numpy as np
import os
from pydub import AudioSegment
import google.generativeai as genai

# Function to get Gemini response
def get_gemini_response(cv_text, job_description, prompt, google_api_key):
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([cv_text, job_description, prompt])
    return response.text

# Function to convert text to speech
def text_to_speech_google(text):
    # Initializing Google Cloud Text-to-Speech client
    client = texttospeech.TextToSpeechClient()

    # Setting up the speech synthesis request
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",  # Specify the language
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    # Sending the speech synthesis request
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Saving the audio data to a file
    with open("output.wav", "wb") as out:
        out.write(response.audio_content)

    return "output.wav"  # Return the path to the saved file

# Function to record audio using sounddevice
def record_audio(filename, duration=5, sample_rate=44100):
    st.info("Recording... Speak now!")

    # Start recording
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.int16)
    sd.wait()  # Wait until recording is finished

    # Save the audio to a WAV file
    sd.write(filename, audio, sample_rate)

    st.info("Recording finished!")
    return filename

def main():
    st.title("Gemini Interviewer")

    cv_text = st.text_area("Enter your CV text")
    job_description = st.text_area("Enter the job description")
    prompt = st.text_area("Enter the prompt for Gemini")

    google_api_key = "YOUR_GOOGLE_API_KEY_HERE"

    if st.button("Generate Gemini Response"):
        st.info("Generating Gemini response...")

        # Getting Gemini response
        gemini_response = get_gemini_response(cv_text, job_description, prompt, google_api_key)
        st.info("Gemini Response Generated.")

        if gemini_response:
            st.text("Gemini Response:")
            st.text(gemini_response)

            # Converting Gemini response to speech
            audio_file = text_to_speech_google(gemini_response)
            st.audio(audio_file, format='audio/wav')

    if st.button("Record Your Voice"):
        audio_file = record_audio("input.wav")
        st.audio(audio_file, format='audio/wav')

if __name__ == "__main__":
    main()
