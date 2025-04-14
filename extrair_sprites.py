import pygame
import os

pygame.init()
# Define um modo de vídeo mínimo para permitir o uso de convert_alpha()
pygame.display.set_mode((1, 1))

def extrair_sprites(sheet_path, rows=4, cols=4, save_folder="animacoes"):
    """
    Extrai os sprites de uma sprite sheet e os salva em uma pasta.
    
    Parâmetros:
        sheet_path: caminho para a sprite sheet (ex: "personagem.png")
        rows, cols: número de linhas e colunas na sprite sheet
        save_folder: pasta onde as imagens serão salvas
    """
    # Cria a pasta se ela não existir
    os.makedirs(save_folder, exist_ok=True)

    # Carrega a imagem completa da sprite sheet
    sheet = pygame.image.load(sheet_path).convert_alpha()

    # Calcula a largura e a altura de cada frame
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // cols
    frame_height = sheet_height // rows

    # Percorre cada linha e coluna para recortar e salvar cada frame
    frame_num = 0
    for row in range(rows):
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height
            # Cria uma superfície para o frame com suporte a transparência
            frame_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surf.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

            # Se quiser tratar o branco como transparente, descomente a linha abaixo:
            # frame_surf.set_colorkey((255, 255, 255))

            # Salva o frame na pasta especificada
            frame_path = os.path.join(save_folder, f"frame_{frame_num}.png")
            pygame.image.save(frame_surf, frame_path)
            frame_num += 1

    print(f"Extração concluída! {frame_num} quadros salvos em '{save_folder}'.")


if __name__ == "__main__":
    # Substitua "personagem.png" pelo nome do seu arquivo de sprite sheet, se necessário
    sprite_sheet = "personagem.png"
    extrair_sprites(sprite_sheet)
    pygame.quit()
