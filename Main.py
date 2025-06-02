import os
import re
import sys
from yt_dlp import YoutubeDL

def intro():
    try:
        with open("ASCII.txt", "r", encoding="utf-8") as f:
            print(f.read())
        print("\nBienvenido al The Pepe's Pirate Ship YouTube ➜ MP4 (Audio + Video)\n")
    except FileNotFoundError:
        print("No se encontró el archivo ASCII.txt")


# 1) Validador
def validar_url(url):
    patron = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$'
    return bool(re.match(patron, url))


# 2) Extrae la información (sin descargar) y devuelve la lista de formatos
def obtener_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        # no descarga aquí, solo extrae info
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('formats', []), info.get('title', 'video')


# 3) Muestra las calidades disponibles (solo video y video+audio mp4/webm) y devuelve un dict mapping opción→format_id
def mostrar_calidades(formatos):
    print("\nFormatos disponibles (solo video / video+audio):")
    opciones = {}
    index = 1

    # Filtra:
    # - formatos con video (vcodec != 'none')
    # - ext sea mp4 o webm (puedes agregar otros si quieres)
    filtrados = [f for f in formatos if f.get('vcodec') != 'none' and f.get('ext') in ('mp4','webm')]
    # Ordena por resolución descendente (si existe), luego por fps
    filtrados.sort(key=lambda x: (
        int(x.get('height') or 0),
        int(x.get('fps') or 0)
    ), reverse=True)

    seen = set()
    for fmt in filtrados:
        # Evita duplicar la misma resolución+fps+ext
        key_repr = f"{fmt.get('height')}x{fmt.get('fps')} {fmt.get('ext')} {fmt.get('acodec')!='none'}"
        if key_repr in seen:
            continue
        seen.add(key_repr)

        # Mostrar datos útiles:
        res = fmt.get('resolution') or f"{fmt.get('width')}x{fmt.get('height')}"
        fps = fmt.get('fps') or '-'
        ext = fmt.get('ext')
        has_audio = (fmt.get('acodec') != 'none')
        size_mb = None
        if fmt.get('filesize') or fmt.get('filesize_approx'):
            size = fmt.get('filesize') or fmt.get('filesize_approx')
            size_mb = round(size / (1024*1024), 1)
        size_str = f"{size_mb} MB" if size_mb else "—"

        tag = fmt.get('format_id')
        opciones[str(index)] = fmt
        print(f"{index}. [{tag}] {res} | fps: {fps} | ext: {ext} | {'con audio' if has_audio else 'solo video'} | {size_str}")
        index += 1

    if not opciones:
        print("   (No se encontraron formatos de video/mp4 o video/webm.)")
    return opciones


# 4) Función que descarga el formato seleccionado (y lo combina con audio si hace falta)
def descargar_con_yt_dlp(url, formato_seleccionado, title):
    # Si el formato contiene audio (acodec != 'none'), basta con ese format_id.
    fmt_id = formato_seleccionado.get('format_id')
    has_audio = formato_seleccionado.get('acodec') != 'none'

    if has_audio:
        format_str = f"{fmt_id}"
    else:
        # Si es video-only, pide el mejor audio disponible en mp4 para luego combinar.
        format_str = f"{fmt_id}+bestaudio[ext=m4a]/best[ext=m4a]/bestaudio"

    # Carpeta de salida = directorio actual
    output_dir = os.getcwd()
    # Limpieza del nombre para evitar caracteres raros
    base = title.replace(" ", "_").replace("/", "_")
    out_template = os.path.join(output_dir, f"{base}.%(ext)s")


    #Opciones de Config
    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',        # obliga a mp4 final
        'outtmpl': out_template,             # guarda en cwd con nombre limpio
        'quiet': False,                      # muestra progreso
        'noprogress': False,
        'no_warnings': True,
        'retries': 3,                        # reintentar 3 veces si falla
    }

    with YoutubeDL(ydl_opts) as ydl:
        print("\n⬇️  Iniciando descarga y posible combinación...")
        ydl.download([url])
        print(f"\nProceso completado. Revisa '{output_dir}' para el archivo terminado.")


if __name__ == "__main__":
    intro()

    # Repetir hasta que se ingrese un link válido o se escriba 'Exit'
    while True:
        url = input("Ingrese un link válido de YouTube (o escriba 'Exit' para salir): ").strip()
        if url.lower() == "exit":
            print("Gracias por usarnoss :).")
            sys.exit(0)
        if validar_url(url):
            break
        print("URL inválida. Inténtalo de nuevo o escribe 'Exit' para salir.\n")

    # 2) Obtener los formatos sin descargar (y título para nombrar el archivo)
    formatos, titulo = obtener_formats(url)

    # 3) Mostrar menú de calidades
    opciones = mostrar_calidades(formatos)
    if not opciones:
        print("No hay formatos de video disponibles para este enlace.")
        sys.exit(1)

    seleccion = input("\nElige la opción deseada (número): ").strip()
    elegido = opciones.get(seleccion)
    if not elegido:
        print("Opción no válida. Saliendo.")
        sys.exit(1)

    # 4) Descargar
    descargar_con_yt_dlp(url, elegido, titulo)


