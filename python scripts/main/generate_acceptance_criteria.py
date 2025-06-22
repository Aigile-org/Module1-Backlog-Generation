import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.generate_ac import *
async def GenerateFinalAC(us):
        myPrompt = constructeInputPromptForACGeneration(us)
        ac= await GenerateACByCUU(us, myPrompt)
        return ac