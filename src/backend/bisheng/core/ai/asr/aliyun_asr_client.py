import asyncio
import os
from typing import Optional

from dashscope.audio.asr import Recognition, RecognitionResult

from ..base import BaseASRClient


class AliyunASRClient(BaseASRClient):
    """Alibaba CloudASRClient"""

    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize Alibaba CloudASRClient
        """

        self.api_key = api_key
        self.recognition = Recognition(
            model=model,
            format="wav",
            sample_rate=16000,
            callback=None,
            **kwargs
        )

    # Time-consuming operation, asynchronous execution
    def sync_func(self, temp_file, language=None, model=None):
        """
        Synchronous recognition function.
        Note: File must exist when calling. Caller is responsible for deleting the file after completion.
        """
        import logging
        logging.info(f"ASR sync_func called with file: {temp_file}, exists: {os.path.exists(temp_file)}")
        
        if not os.path.exists(temp_file):
            raise FileNotFoundError(f"Audio file not found: {temp_file}. This is a race condition bug.")
        
        try:
            result: RecognitionResult = self.recognition.call(temp_file, api_key=self.api_key, language=language,
                                                              model=model)
            return result
        finally:
            # Clean up temporary file after processing
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logging.info(f"ASR temp file deleted: {temp_file}")

    async def _transcribe(
            self,
            audio: str,
            language: Optional[str] = None,
            model: Optional[str] = None,
            **kwargs
    ) -> str:
        import logging
        logging.info(f"ASR _transcribe START with file: {audio}, exists: {os.path.exists(audio)}")
        
        # Use run_in_executor to ensure sync_func completes before file deletion
        loop = asyncio.get_event_loop()
        result: RecognitionResult = await loop.run_in_executor(None, self.sync_func, audio, language, model)
        
        logging.info(f"ASR _transcribe DONE, status: {result.status_code if result else 'None'}")
        
        if result.status_code != 200:
            raise RuntimeError(
                f"ASR request failed with status code {result.code} and message {result.message}"
            )

        sentence = result.get_sentence()
        if sentence and sentence[0]:
            return sentence[0]["text"]
        return ""
