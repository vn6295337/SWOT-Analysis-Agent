# A2A Strategy Agent Deployment Guide

## Overview

This guide explains the different deployment configurations available for the A2A Strategy Agent.

## Deployment Modes

### 1. Full Featured (Default)
- Includes all LangChain/LangGraph dependencies
- Full SWOT analysis capabilities
- Requires all API keys (Groq, Tavily, LangSmith)

### 2. Minimal Standalone
- No external API dependencies
- Lightweight implementation
- Ideal for offline use or testing

### 3. Hugging Face Spaces Optimized
- Optimized for HF Spaces environment
- Reduced dependencies for faster deployment
- Configured for HF Spaces constraints

## Requirements

### Base Requirements
```bash
pip install -r configs/base_requirements.txt
```

### Full Requirements
```bash
pip install -r configs/full_requirements.txt
```

### HF Spaces Requirements
```bash
pip install -r configs/hf_spaces_requirements.txt
```

## Starting the Service

### Using Unified Script
```bash
# Full mode (default)
./configs/start_unified.sh

# Minimal mode
./configs/start_unified.sh minimal

# HF Spaces mode
./configs/start_unified.sh hf_spaces
```

### Using Environment Variables
```bash
# Set mode via environment variable
export DEPLOYMENT_MODE=minimal
./configs/start_unified.sh
```

## Configuration

Set the following environment variables in your `.env` file:

```
DEPLOYMENT_MODE=full|minimal|hf_spaces
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
```
