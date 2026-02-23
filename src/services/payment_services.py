import razorpay 
import os
from src.core.config import Config

client =razorpay.Client(auth=(Config.RAZORPAY_KEY_ID ,Config.RAZORPAY_KEY_SECRET))