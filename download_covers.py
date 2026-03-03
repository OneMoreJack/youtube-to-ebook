import os
import urllib.request
import concurrent.futures

covers = [
    ("6_nature", "https://images.unsplash.com/photo-1506744626753-eba7bc36130e?q=80&w=320&h=480&fit=crop"),
    ("7_city", "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?q=80&w=320&h=480&fit=crop"),
    ("8_abstract2", "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?q=80&w=320&h=480&fit=crop"),
    ("9_space", "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=320&h=480&fit=crop"),
    ("10_ocean", "https://images.unsplash.com/photo-1518837695005-2083093ee35b?q=80&w=320&h=480&fit=crop"),
    ("11_mountain2", "https://images.unsplash.com/photo-1493246507139-91e8fad9978e?q=80&w=320&h=480&fit=crop"),
    ("12_arch", "https://images.unsplash.com/photo-1483728642387-6c3ba6c62772?q=80&w=320&h=480&fit=crop"),
    ("13_min", "https://images.unsplash.com/photo-1508614589041-895b88991e3e?q=80&w=320&h=480&fit=crop"),
    ("14_grad1", "https://images.unsplash.com/photo-1557682250-33bd709cbe85?q=80&w=320&h=480&fit=crop"),
    ("15_grad2", "https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=320&h=480&fit=crop"),
    ("16_art", "https://images.unsplash.com/photo-1604871000636-074fa5117945?q=80&w=320&h=480&fit=crop"),
    ("17_3d", "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=320&h=480&fit=crop"),
    ("18_road", "https://images.unsplash.com/photo-1501696461415-6bd6660c6742?q=80&w=320&h=480&fit=crop"),
    ("19_leaves", "https://images.unsplash.com/photo-1528459801416-a9e53bbf4e17?q=80&w=320&h=480&fit=crop"),
    ("20_neon", "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?q=80&w=320&h=480&fit=crop")
]

os.makedirs("default_covers", exist_ok=True)

def download(item):
    name, url = item
    path = f"default_covers/{name}.jpg"
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        urllib.request.urlretrieve(url, path)

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    ex.map(download, covers)
print("Done")
