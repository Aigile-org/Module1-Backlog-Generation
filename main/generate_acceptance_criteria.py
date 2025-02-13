import sys
import os
import asyncio

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from helpers.generate_ac import *
async def GenerateFinalAC(us):
        # print("-" * 70)
        # print(us)

        myPrompt = constructeInputPromptForACGeneration(us)

        ac= await GenerateACByCUU(us, myPrompt)
        # print("=" * 20 + "AC for Group " + projectNo + "=" * 20)
        # print(ac)
        return ac
        # usNo = str(usNo)
        # writeACbyProject(us, ac, projectNo, usNo)
        # processFinalACbyProject(us, projectNo, usNo, ratio)


# ratio = 0.85
# us="As a user, I want to view thumbnail sequences of video segments."
# acceptance_criterias=asyncio.run(GenerateFinalAC(us))
# appended=AppendingStoriesFromCUU(acceptance_criterias.splitlines())
# print(len(appended))
# filtered=filterSimilarAC(appended,ratio)
# print(filtered)
# print(len(filtered))