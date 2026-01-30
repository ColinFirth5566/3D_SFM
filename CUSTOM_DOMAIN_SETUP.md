# 🌐 Custom Domain Setup: yfcosmos.com

Your 3D reconstruction website is now configured for **yfcosmos.com**!

## ✅ Changes Made

1. ✅ Removed basePath from Next.js config (no longer using `/3D_SFM`)
2. ✅ Created CNAME file pointing to `yfcosmos.com`
3. ✅ Updated backend CORS to allow requests from `yfcosmos.com`
4. ✅ Updated GitHub Actions workflow to include CNAME in deployment

## 🔧 DNS Configuration Required

To make your custom domain work, you need to configure DNS records with your domain registrar.

### Option 1: Apex Domain (Recommended)

Configure these DNS records at your domain registrar:

```
Type    Name    Value
A       @       185.199.108.153
A       @       185.199.109.153
A       @       185.199.110.153
A       @       185.199.111.153
```

### Option 2: WWW Subdomain

```
Type     Name    Value
CNAME    www     colinfirth5566.github.io
```

### Option 3: Both (Best Practice)

Use Option 1 for apex domain, plus:

```
Type     Name    Value
CNAME    www     yfcosmos.com
```

## 🚀 GitHub Pages Configuration

After DNS is configured:

1. Go to: https://github.com/ColinFirth5566/3D_SFM/settings/pages
2. Under "Custom domain", enter: `yfcosmos.com`
3. Click "Save"
4. ✅ Check "Enforce HTTPS" (after DNS propagates, ~24 hours)

## 📋 Deployment Steps

1. **Push the changes** (already triggered)
2. **Configure DNS** at your domain registrar
3. **Set custom domain** in GitHub Pages settings
4. **Wait for DNS propagation** (5 minutes - 48 hours, usually ~1 hour)
5. **Enable HTTPS** in GitHub settings (after DNS propagates)

## 🌐 Final URLs

Once configured:

- **Primary**: https://yfcosmos.com
- **WWW**: https://www.yfcosmos.com (if configured)
- **Fallback**: https://colinfirth5566.github.io/3D_SFM/

## 🔍 DNS Propagation Check

After configuring DNS, check propagation status:

```bash
# Check A records
dig yfcosmos.com A

# Check CNAME records
dig www.yfcosmos.com CNAME

# Or use online tools:
# https://www.whatsmydns.net/#A/yfcosmos.com
```

## 📝 Domain Registrar Examples

### Cloudflare
1. Dashboard → DNS → Records
2. Add A records (proxied or DNS only)
3. Disable "Always Use HTTPS" temporarily until GitHub HTTPS is enabled

### GoDaddy
1. Domain Settings → DNS → Records
2. Add A records with values above
3. TTL: 600 seconds (default)

### Namecheap
1. Domain List → Manage → Advanced DNS
2. Add A records as "A Record"
3. Host: @ | Value: GitHub IPs

### Google Domains
1. DNS → Resource records
2. Add A records
3. Name: @ | Type: A | Data: GitHub IPs

## ⚠️ Common Issues

### Issue: DNS not propagating
**Solution**: Wait 1-24 hours, check with `dig` or whatsmydns.net

### Issue: Certificate error
**Solution**: Wait for DNS to fully propagate before enabling HTTPS

### Issue: 404 error
**Solution**: Verify CNAME file exists in deployment (check Actions logs)

### Issue: CORS error
**Solution**: Backend CORS is configured, make sure backend is running

## 🎯 Testing

Once DNS propagates:

1. Visit: https://yfcosmos.com
2. You should see the 3D reconstruction website
3. Start backend: `cd backend && python main.py`
4. Upload images and test reconstruction

## 📊 Status

- ✅ Code configured for custom domain
- ✅ CNAME file created
- ✅ CORS updated
- ✅ Workflow updated
- ⏳ DNS configuration (you need to do this)
- ⏳ GitHub Pages custom domain setting (after DNS)
- ⏳ HTTPS enforcement (after DNS propagates)

---

Your website will be live at **https://yfcosmos.com** once DNS is configured! 🚀
