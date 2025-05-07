import os
from PIL import Image

def remove_background_using_corner(image_path, output_path=None, threshold=30):
    """
    Remove o fundo de uma imagem PNG, pegando a cor do pixel no canto superior esquerdo
    e tornando transparentes todos os pixels com cor próxima (dentro de `threshold`).
    """
    img = Image.open(image_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # Cor de fundo: pixel mais alto e à esquerda
    bg_color = pixels[0, 0][:3]

    def is_similar(c1, c2, thresh):
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2]) <= thresh

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if is_similar((r, g, b), bg_color, threshold):
                pixels[x, y] = (r, g, b, 0)  # torna transparente

    save_path = output_path or image_path
    img.save(save_path)
    print(f"Processado: {save_path}")

def main():
    folder = "."
    # Você pode ajustar o threshold aqui se quiser:
    threshold = 60

    for filename in os.listdir(folder):
        if filename.lower().endswith(".png"):
            remove_background_using_corner(filename, threshold=threshold)

if __name__ == "__main__":
    main()
