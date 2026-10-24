from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io#helps in handling byte streams, allowing us to read audio data from bytes rather than files
import librosa#used for audio processing, including loading audio files, extracting features, and performing various transformations
import streamlit as st

@st.cache_resource
def load_voice_encoder():
    encoder = VoiceEncoder()
    return encoder
def get_voice_embedding(audio_bytes):#
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)#gives embedding of audio in 256D
        return embedding.tolist()  # Convert to list for easier storage and comparison
    
    except Exception as e:
        st.error("Voice recognition failed. Please ensure the audio is clear and try again.")
        return None
    
def identify_specker(new_embedding,candidates_dict,threshold=0.65):#
    if new_embedding is None or not candidates_dict:
        return None,0.0
    
    best_sid=None
    best_score=-1.0
    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:#if stored embedding present 
            similarity = np.dot(new_embedding, stored_embedding) #gives similarity score
            if similarity>best_score:
                best_score=similarity
                best_sid=sid #student id
    
    if best_score>=threshold:
        return best_sid,best_score
    return None,best_score
           
def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)
        
        identified_results = {}
        
        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)
            
            sid, score = identify_specker(embedding, candidates_dict, threshold)
            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score
        return identified_results
    except Exception as e:
        st.error("Bulk Process error")
        return {}