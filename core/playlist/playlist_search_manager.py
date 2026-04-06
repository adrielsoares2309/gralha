import difflib
import unicodedata


class PlaylistSearchManager:
    """Responsavel por indexar e filtrar musicas dentro de uma playlist."""

    def __init__(self, musicas=None):
        self._entries = []
        self.set_musicas(musicas or [])

    def set_musicas(self, musicas):
        self._entries = []
        for musica in musicas:
            nome = getattr(musica, "nome", "") or ""
            artista = getattr(musica, "artista", "") or ""
            album = getattr(musica, "album", "") or ""

            campos = [nome, artista, album]
            texto_busca = " ".join(campo for campo in campos if campo)
            texto_normalizado = self.normalize(texto_busca)
            palavras = [parte for parte in texto_normalizado.split() if parte]

            self._entries.append(
                {
                    "musica": musica,
                    "texto": texto_normalizado,
                    "palavras": palavras,
                }
            )

    def filter(self, query):
        consulta = self.normalize(query)
        if not consulta:
            return [entry["musica"] for entry in self._entries]

        termos = [parte for parte in consulta.split() if parte]
        if not termos:
            return [entry["musica"] for entry in self._entries]

        resultados = []
        for entry in self._entries:
            if self._matches_entry(entry, consulta, termos):
                resultados.append(entry["musica"])
        return resultados

    @staticmethod
    def normalize(texto):
        texto = unicodedata.normalize("NFKD", str(texto or ""))
        texto = "".join(char for char in texto if not unicodedata.combining(char))
        return " ".join(texto.casefold().split())

    def _matches_entry(self, entry, consulta, termos):
        texto = entry["texto"]
        if consulta in texto:
            return True

        palavras = entry["palavras"]
        for termo in termos:
            if termo in texto:
                continue
            if any(palavra.startswith(termo) for palavra in palavras):
                continue
            if difflib.get_close_matches(termo, palavras, n=1, cutoff=0.84):
                continue
            return False

        return True
