"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
import sys, os



def googleListLanguages():
	client = texttospeech.TextToSpeechClient()
	voices = client.list_voices().voices
	languages = googleUniqueLanguagesFromVoices(voices)
	print(f' Languages: {len(languages)} '.center(60, '-'))
	for i, language in enumerate(sorted(languages)):
		print(f'{language:>10}', end='' if i % 5 < 4 else '\n')

def googleUniqueLanguagesFromVoices(voices):
	language_set = set()
	for voice in voices:
		for language_code in voice.language_codes:
				language_set.add(language_code)
	return language_set

def googleListVoices(language_code=None):
	client = texttospeech.TextToSpeechClient()
	response = client.list_voices(language_code=language_code)
	voices = sorted(response.voices, key=lambda voice: voice.name)
	print(f' Voices: {len(voices)} '.center(60, '-'))
	for voice in voices:
		languages = ', '.join(voice.language_codes)
		name = voice.name
		gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
		rate = voice.natural_sample_rate_hertz
		print(f'{languages:<8}',
			f'{name:<24}',
			f'{gender:<8}',
			f'{rate:,} Hz',
			sep=' | ')

'''
writeGoogleAudio('en-GB-Standard-B', "The songs you want to hear, when you want to hear them, GCS radio lIve")
>>> googleListVoices("en")
------------------------ Voices: 44 ------------------------
en-AU    | en-AU-Standard-A         | FEMALE   | 24,000 Hz
en-AU    | en-AU-Standard-B         | MALE     | 24,000 Hz
en-AU    | en-AU-Standard-C         | FEMALE   | 24,000 Hz
en-AU    | en-AU-Standard-D         | MALE     | 24,000 Hz
en-AU    | en-AU-Wavenet-A          | FEMALE   | 24,000 Hz
en-AU    | en-AU-Wavenet-B          | MALE     | 24,000 Hz
en-AU    | en-AU-Wavenet-C          | FEMALE   | 24,000 Hz
en-AU    | en-AU-Wavenet-D          | MALE     | 24,000 Hz
en-GB    | en-GB-Standard-A         | FEMALE   | 24,000 Hz
en-GB    | en-GB-Standard-B         | MALE     | 24,000 Hz
en-GB    | en-GB-Standard-C         | FEMALE   | 24,000 Hz
en-GB    | en-GB-Standard-D         | MALE     | 24,000 Hz
en-GB    | en-GB-Standard-F         | FEMALE   | 24,000 Hz
en-GB    | en-GB-Wavenet-A          | FEMALE   | 24,000 Hz
en-GB    | en-GB-Wavenet-B          | MALE     | 24,000 Hz
en-GB    | en-GB-Wavenet-C          | FEMALE   | 24,000 Hz
en-GB    | en-GB-Wavenet-D          | MALE     | 24,000 Hz
en-GB    | en-GB-Wavenet-F          | FEMALE   | 24,000 Hz
en-IN    | en-IN-Standard-A         | FEMALE   | 24,000 Hz
en-IN    | en-IN-Standard-B         | MALE     | 24,000 Hz
en-IN    | en-IN-Standard-C         | MALE     | 24,000 Hz
en-IN    | en-IN-Standard-D         | FEMALE   | 24,000 Hz
en-IN    | en-IN-Wavenet-A          | FEMALE   | 24,000 Hz
en-IN    | en-IN-Wavenet-B          | MALE     | 24,000 Hz
en-IN    | en-IN-Wavenet-C          | MALE     | 24,000 Hz
en-IN    | en-IN-Wavenet-D          | FEMALE   | 24,000 Hz
en-US    | en-US-Standard-B         | MALE     | 24,000 Hz
en-US    | en-US-Standard-C         | FEMALE   | 24,000 Hz
en-US    | en-US-Standard-D         | MALE     | 24,000 Hz
en-US    | en-US-Standard-E         | FEMALE   | 24,000 Hz
en-US    | en-US-Standard-G         | FEMALE   | 24,000 Hz
en-US    | en-US-Standard-H         | FEMALE   | 24,000 Hz
en-US    | en-US-Standard-I         | MALE     | 24,000 Hz
en-US    | en-US-Standard-J         | MALE     | 24,000 Hz
en-US    | en-US-Wavenet-A          | MALE     | 24,000 Hz
en-US    | en-US-Wavenet-B          | MALE     | 24,000 Hz
en-US    | en-US-Wavenet-C          | FEMALE   | 24,000 Hz
en-US    | en-US-Wavenet-D          | MALE     | 24,000 Hz
en-US    | en-US-Wavenet-E          | FEMALE   | 24,000 Hz
en-US    | en-US-Wavenet-F          | FEMALE   | 24,000 Hz
en-US    | en-US-Wavenet-G          | FEMALE   | 24,000 Hz
en-US    | en-US-Wavenet-H          | FEMALE   | 24,000 Hz
en-US    | en-US-Wavenet-I          | MALE     | 24,000 Hz
en-US    | en-US-Wavenet-J          | MALE     | 24,000 Hz

Good ones for radio:
		"en-US-Wavenet-B",
		"en-US-Wavenet-D",
		"en-IN-Wavenet-C",
		"ar-XA-Wavenet-C",
		"da-DK-Wavenet-C",
		"en-AU-Wavenet-B",
		"en-AU-Wavenet-C",
		"en-GB-Wavenet-F",
		"en-GB-Wavenet-B",
		"en-GB-Wavenet-D",
		"fr-CA-Wavenet-B",
		"fr-CA-Wavenet-D",
		"fr-FR-Wavenet-B",
		"it-IT-Wavenet-D",
		"nb-NO-Wavenet-D",
		"pl-PL-Wavenet-E",
		"sv-SE-Wavenet-A",
		"vi-VN-Wavenet-D",
		"tr-TR-Wavenet-E",
		"ja-JP-Wavenet-D",
		"ja-JP-Wavenet-D",
		"ko-KR-Wavenet-B",
'''
def writeGoogleAudio(voice_name, fn, text):

	language_code = '-'.join(voice_name.split('-')[:2])
	text_input = texttospeech.SynthesisInput(text=text)
	voice_params = texttospeech.VoiceSelectionParams(
		language_code=language_code,
		name=voice_name)
	audio_config = texttospeech.AudioConfig(
		audio_encoding=texttospeech.AudioEncoding.MP3)

	client = texttospeech.TextToSpeechClient()
	response = client.synthesize_speech(
		input=text_input,
		voice=voice_params,
		audio_config=audio_config)

	filename = f'{fn}.mp3'
	with open(filename, 'wb') as out:
		out.write(response.audio_content)
		print(f'Audio content written to "{filename}"')

googleRadioVoices = [
	"en-US-Wavenet-B",
	"en-US-Wavenet-D",
	"en-IN-Wavenet-C",
	"en-AU-Wavenet-B",
	"en-AU-Wavenet-C",
	"en-GB-Wavenet-F",
	"en-GB-Wavenet-B",
	"en-GB-Wavenet-D",
	"ar-XA-Wavenet-C",
	"da-DK-Wavenet-C",
	"fr-CA-Wavenet-B",
	"fr-CA-Wavenet-D",
	"fr-FR-Wavenet-B",
	"it-IT-Wavenet-D",
	"nb-NO-Wavenet-D",
	"pl-PL-Wavenet-E",
	"sv-SE-Wavenet-A",
	"vi-VN-Wavenet-D",
	"tr-TR-Wavenet-E",
	"ja-JP-Wavenet-D",
	"ja-JP-Wavenet-D",
	"ko-KR-Wavenet-B"]
googlePrimaryVoices = googleRadioVoices[:8]
