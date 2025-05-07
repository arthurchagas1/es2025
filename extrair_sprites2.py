import pygame
import os

pygame.init()
# “Hack” mínimo para habilitar convert_alpha()
pygame.display.set_mode((1, 1))

def extrair_sprites(
        sheet_path: str,
        rows: int = 4,           # ← quantas LINHAS você quer extrair
        cols: int = 6,           # ← quantas COLUNAS você quer extrair
        start_row: int = 0,      # ← caso queira pular linhas no topo da sheet
        save_folder: str = "animacoes_meira"
    ) -> None:
    """
    Recorta sprites de uma sprite‑sheet e salva cada frame como PNG.

    Parâmetros
    ----------
    sheet_path : str
        Caminho da sprite‑sheet (ex.: "personagem.png").
    rows : int
        Número de linhas a extrair (padrão = 4).
    cols : int
        Número de colunas a extrair (padrão = 7).
    start_row : int
        Linha inicial (0 = primeira linha da imagem).
    save_folder : str
        Pasta de destino para os frames salvos.
    """
    # Garante a existência da pasta de destino
    os.makedirs(save_folder, exist_ok=True)

    # Carrega a imagem completa
    sheet = pygame.image.load(sheet_path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()

    # Calcula a largura e a altura de cada quadro
    frame_width  = sheet_width  // cols
    frame_height = sheet_height // (rows + start_row)

    frame_num = 0
    for row in range(start_row, start_row + rows):
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height

            # Cria superfície transparente para o frame
            frame_surf = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surf.blit(sheet, (0, 0), (x, y, frame_width, frame_height))

            # Salva o frame
            frame_path = os.path.join(save_folder, f"frame_{frame_num}.png")
            pygame.image.save(frame_surf, frame_path)
            frame_num += 1

    print(f"Extração concluída! {frame_num} quadros salvos em '{save_folder}'.")


if __name__ == "__main__":
    sprite_sheet = "meira.png"          # <-- altere para o nome correto do arquivo
    extrair_sprites(sprite_sheet, rows=4, cols=6)  # ← 28 sprites (4×7)
    pygame.quit()
