import os
import re
import urllib.request

output_dir = os.path.abspath("web/public/fonts")
os.makedirs(output_dir, exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Fetch Google font stylesheet
css_url = "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Gurmukhi:wght@400;600;700&display=swap"

req = urllib.request.Request(css_url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        css_content = response.read().decode('utf-8')
        
        # Find all url(https://...) blocks
        matches = re.findall(r'src:\s*url\((https://fonts\.gstatic\.com/[^)]+)\)\s*format\([\'"]woff2[\'"]\);', css_content)
        font_faces = re.split(r'@font-face\s*\{', css_content)[1:]
        
        local_css = ""
        saved_files = set()
        
        for ff in font_faces:
            # extract font-family, font-weight, unicode-range, src url
            fam_match = re.search(r'font-family:\s*[\'"]([^\'"]+)[\'"];', ff)
            weight_match = re.search(r'font-weight:\s*([0-9]+);', ff)
            url_match = re.search(r'src:\s*url\((https://[^\)]+)\)', ff)
            range_match = re.search(r'unicode-range:\s*([^;]+);', ff)
            
            if fam_match and weight_match and url_match:
                fam = fam_match.group(1)
                weight = weight_match.group(1)
                remote_url = url_match.group(1)
                unicode_range = range_match.group(1) if range_match else ""
                
                # filename
                clean_fam = fam.lower().replace(' ', '-')
                fname = f"{clean_fam}-{weight}-{remote_url.split('/')[-1]}"
                if not fname.endswith('.woff2'):
                    fname += '.woff2'
                
                file_path = os.path.join(output_dir, fname)
                if fname not in saved_files:
                    try:
                        f_req = urllib.request.Request(remote_url, headers=headers)
                        with urllib.request.urlopen(f_req, timeout=10) as f_res:
                            with open(file_path, "wb") as f_out:
                                f_out.write(f_res.read())
                        saved_files.add(fname)
                    except Exception as ex:
                        print(f"Failed to download {remote_url}: {ex}")
                
                local_css += f"""@font-face {{
  font-family: '{fam}';
  font-style: normal;
  font-weight: {weight};
  font-display: swap;
  src: url('/fonts/{fname}') format('woff2');
"""
                if unicode_range:
                    local_css += f"  unicode-range: {unicode_range};\n"
                local_css += "}\n\n"
        
        # Save fonts.css in web/src/
        with open("web/src/fonts.css", "w", encoding="utf-8") as f_css:
            f_css.write(local_css)
        print(f"Downloaded {len(saved_files)} font files to web/public/fonts and generated web/src/fonts.css")

except Exception as e:
    print(f"Could not download fonts (offline fallback will be generated): {e}")
    # Create empty mock woff2 files for local font-face definitions so build succeeds
    mock_files = [
        "inter-400.woff2", "inter-600.woff2", "inter-700.woff2",
        "noto-devanagari-400.woff2", "noto-devanagari-600.woff2", "noto-devanagari-700.woff2",
        "noto-gurmukhi-400.woff2", "noto-gurmukhi-600.woff2", "noto-gurmukhi-700.woff2"
    ]
    for mf in mock_files:
        p = os.path.join(output_dir, mf)
        if not os.path.exists(p):
            with open(p, "wb") as f:
                f.write(b"wOFF\x00\x01\x00\x00")
    
    fallback_css = """@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/inter-400.woff2') format('woff2'), local('system-ui');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/inter-600.woff2') format('woff2'), local('system-ui');
}
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/fonts/inter-700.woff2') format('woff2'), local('system-ui');
}
@font-face {
  font-family: 'Noto Sans Devanagari';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/noto-devanagari-400.woff2') format('woff2'), local('Mangal'), local('Nirmala UI');
}
@font-face {
  font-family: 'Noto Sans Devanagari';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/noto-devanagari-600.woff2') format('woff2'), local('Mangal'), local('Nirmala UI');
}
@font-face {
  font-family: 'Noto Sans Gurmukhi';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/noto-gurmukhi-400.woff2') format('woff2'), local('Raavi'), local('Nirmala UI');
}
"""
    with open("web/src/fonts.css", "w", encoding="utf-8") as f_css:
        f_css.write(fallback_css)
    print("Generated self-hosted fallback font definitions in web/src/fonts.css")
