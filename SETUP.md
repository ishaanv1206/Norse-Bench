# Setup Instructions

## Prerequisites

- Python 3.12 or higher
- Groq API keys (obtain from https://console.groq.com/)

## Installation

1. Install required packages:
```bash
py -m pip install -r requirements.txt
```

2. Configure API keys:
   - Copy `.env.example` to `.env`
   - Add your Groq API keys to the `.env` file
   - You can add multiple keys for automatic rotation on rate limits

Example `.env` file:
```
GROQ_API_KEY_1=gsk_your_first_key_here
GROQ_API_KEY_2=gsk_your_second_key_here
GROQ_API_KEY_3=gsk_your_third_key_here
```

## Verification

Verify all packages are installed correctly:
```bash
py -c "import norsecorpus, dotenv, groq, pandas, matplotlib, seaborn, tqdm, hypothesis; print('All packages imported successfully')"
```

## Next Steps

After setup is complete, you can proceed with implementing the data acquisition and text processing components.
