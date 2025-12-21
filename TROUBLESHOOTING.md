# 🛠️ Comprehensive Troubleshooting Guide

## 🔍 Current Issue: "Failed to start analysis"

This error occurs when the frontend cannot connect to the backend API. Here's how to fix it:

## 🚀 Step-by-Step Solutions

### 1. **Verify the API is Running**

Run the test script:
```bash
python test_api_connection.py
```

**Expected output:**
```
✅ Health check passed: {'status': 'healthy', ...}
✅ Analysis endpoint works!
🎉 API is working perfectly!
```

**If you get errors:**
- ❌ "Could not connect to API" - API is not running
- ❌ "Health check failed" - API is running but unhealthy
- ❌ "Analysis endpoint failed" - API has issues with analysis

### 2. **Check API Process**

```bash
# Check if API process is running
ps aux | grep python

# If not running, start it manually
python api_standalone.py
```

### 3. **Test API Endpoints Manually**

```bash
# Test health endpoint
curl http://localhost:8002/api/health

# Test analysis endpoint
curl -X POST http://localhost:8002/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Tesla"}'
```

### 4. **Check Port Availability**

```bash
# Check if port 8002 is in use
netstat -tuln | grep 8002

# Or on macOS
lsof -i :8002
```

### 5. **Verify File Permissions**

```bash
# Make sure scripts are executable
chmod +x start_minimal.sh
chmod +x api_standalone.py

# Check file permissions
ls -la api_standalone.py
```

## 🔧 Common Issues and Fixes

### Issue: API not starting at all

**Symptoms:**
- No output when running `python api_standalone.py`
- Process dies immediately

**Solutions:**
1. **Check Python version:**
   ```bash
   python --version  # Should be 3.7+
   ```

2. **Install required packages:**
   ```bash
   pip install fastapi uvicorn
   ```

3. **Check for syntax errors:**
   ```bash
   python -m py_compile api_standalone.py
   ```

### Issue: API starts but doesn't respond

**Symptoms:**
- API process is running
- But requests time out or fail

**Solutions:**
1. **Check port binding:**
   ```bash
   # Try binding to 0.0.0.0 instead of localhost
   python api_standalone.py
   ```

2. **Check firewall settings:**
   ```bash
   # Make sure port 8002 is open
   sudo ufw allow 8002
   ```

3. **Test with different port:**
   ```bash
   # Modify api_standalone.py to use port 8003
   PORT=8003 python api_standalone.py
   ```

### Issue: CORS errors

**Symptoms:**
- Browser shows CORS errors
- API works with curl but not from frontend

**Solutions:**
1. **Verify CORS middleware is enabled** (it is in our code)
2. **Test from same origin** (both frontend and API on same domain)
3. **Use proxy in development**

## 🎯 Hugging Face Space Specific Issues

### Issue: Space not building

**Symptoms:**
- Build fails in HF Space
- "Job failed with exit code: 1"

**Solutions:**
1. **Use minimal Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   COPY . .
   RUN pip install fastapi uvicorn
   CMD ["python", "api_standalone.py"]
   ```

2. **Check Space logs:**
   - Go to Space settings
   - Check build logs for specific errors

3. **Reduce Docker layers:**
   - Combine RUN commands
   - Use smaller base image

### Issue: Space starts but API not accessible

**Symptoms:**
- Space shows "Running"
- But API endpoints don't work

**Solutions:**
1. **Check Space port configuration:**
   - Should be port 8002
   - Verify in Space settings

2. **Test with public URL:**
   ```bash
   curl https://your-space-name.hf.space/api/health
   ```

3. **Check Space secrets:**
   - Even though our API doesn't need keys, HF might require them

## 📋 Final Checklist

- [ ] API starts without errors
- [ ] Health endpoint responds (GET /api/health)
- [ ] Analysis endpoint works (POST /api/analyze)
- [ ] Port 8002 is accessible
- [ ] No firewall blocking connections
- [ ] CORS headers are properly set
- [ ] All files have correct permissions
- [ ] Python environment has required packages

## 💡 Pro Tips

1. **Always test locally first** before deploying to Space
2. **Use minimal configuration** for HF Spaces
3. **Check logs systematically** for specific error messages
4. **Test endpoints individually** to isolate issues
5. **Start with health check** before testing complex endpoints

If you're still having issues, the error is likely in the Space configuration rather than the code itself.