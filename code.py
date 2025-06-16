def filter_m3u(content: str) -> str:
    print("🔍 Filtering and categorizing channels...")
    lines = content.splitlines()
    filtered = []
    total = len(lines)
    i = 0

    while i < total:
        line = lines[i]
        if line.startswith("#EXTINF"):
            url = lines[i + 1] if i + 1 < total else ""
            matched = False

            # Extract channel name
            name_match = re.search(r",(.*)", line)
            channel_name = name_match.group(1).strip() if name_match else ""

            # Clean and reconstruct the EXTINF line
            for category, patterns in categories.items():
                if any(pattern.search(line) for pattern in patterns):
                    # Clean old group-title
                    line = re.sub(r'group-title="[^"]*"', '', line)

                    # Ensure -1 is directly after EXTINF
                    line = re.sub(r'#EXTINF[^:]*:', '#EXTINF:-1', line)

                    # Add group-title back in
                    if 'group-title=' not in line:
                        line = line.replace('#EXTINF:-1', f'#EXTINF:-1 group-title="{category}"')

                    # Ensure one comma, one space before channel name
                    line = re.sub(r",(?! )", ", ", line)

                    # Append cleaned channel
                    filtered.extend([line.strip(), url.strip()])
                    matched = True
                    break

            i += 2 if matched else 1
        else:
            i += 1

    print(f"✅ Filtered and categorized {len(filtered)//2} channels.")
    return "#EXTM3U\n" + "\n".join(filtered)
