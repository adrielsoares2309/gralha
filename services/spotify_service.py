import os
import time

import requests
from spotipy.cache_handler import MemoryCacheHandler

from dotenv import load_dotenv

load_dotenv()

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:  # pragma: no cover
    spotipy = None
    SpotifyClientCredentials = None


class SpotifyService:
    """Consulta metadados de faixas usando a API do Spotify."""

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
        self._client = None
        self._client_criado_em = 0
        self._client_ttl = 3000  # 50 minutos (token dura 60min, margem de segurança)
        self._cache = {}
        self._cache_ttl = 600  # 10 minutos para cache de buscas

    class _DebugSession(requests.Session):
        @staticmethod
        def _redigir_headers(headers):
            headers_seguros = {}
            for chave, valor in (headers or {}).items():
                if chave.lower() == "authorization" and isinstance(valor, str):
                    tipo, _, _ = valor.partition(" ")
                    headers_seguros[chave] = f"{tipo} ***" if tipo else "***"
                else:
                    headers_seguros[chave] = valor
            return headers_seguros

        def request(self, method, url, **kwargs):
            headers = self._redigir_headers(kwargs.get("headers"))
            print("REQUEST:", method, url)
            print("HEADERS:", headers)

            response = super().request(method, url, **kwargs)

            print("RESPONSE STATUS:", response.status_code)
            print("RESPONSE BODY:", response.text)
            return response

    # ------------------------------------------------------------------
    # Busca simples (retorna 1 resultado)
    # ------------------------------------------------------------------

    def buscar_musica(self, query):
        termo = (query or "").strip()
        if not termo or not self.client_id or not self.client_secret:
            return None

        cache_key = termo.casefold()
        resultado_cache = self._cache.get(cache_key)
        if resultado_cache and time.time() < resultado_cache["expira_em"]:
            return resultado_cache["dados"]

        client = self._get_client()
        if client is None:
            return None

        try:
            resultado = self._buscar_com_retry(client, f"track:{termo}", limit=1)
            itens = resultado.get("tracks", {}).get("items", [])

            if not itens:
                resultado = self._buscar_com_retry(client, termo, limit=1)
                itens = resultado.get("tracks", {}).get("items", [])

            if not itens:
                self._salvar_cache(cache_key, None)
                return None

            metadata = self._parse_track(itens[0])
            self._salvar_cache(cache_key, metadata)
            return metadata

        except Exception as exc:
            print("SPOTIFY ERROR:", exc)
            return None

    # ------------------------------------------------------------------
    # Busca múltipla (retorna lista)
    # ------------------------------------------------------------------

    def buscar_musicas(self, query, limit=5):
        termo = (query or "").strip()
        if not termo or not self.client_id or not self.client_secret:
            return []

        client = self._get_client()
        if client is None:
            return []

        try:
            resultado = self._buscar_com_retry(client, f"track:{termo}", limit=limit)
            itens = resultado.get("tracks", {}).get("items", [])

            if not itens:
                resultado = self._buscar_com_retry(client, termo, limit=limit)
                itens = resultado.get("tracks", {}).get("items", [])

            return [self._parse_track(item) for item in itens]

        except Exception as exc:
            print("SPOTIFY ERROR:", exc)
            return []

    # ------------------------------------------------------------------
    # Interno: busca com retry automático se token expirou (401/403)
    # ------------------------------------------------------------------

    def _buscar_com_retry(self, client, query, limit):
        try:
            return client.search(q=query, type="track", limit=limit)
        except Exception as exc:
            codigo = getattr(exc, "http_status", None)
            mensagem = str(exc)
            if codigo == 401:
                print(
                    "SPOTIFY: received HTTP 401; retrying with a fresh client."
                )
                self._invalidar_cliente()
                client = self._get_client()
                if client is None:
                    raise
                print("SPOTIFY: token refreshed")
                return client.search(q=query, type="track", limit=limit)
            if codigo == 403:
                if "Active premium subscription required for the owner of the app" in mensagem:
                    print(
                        "SPOTIFY: access forbidden by Spotify. "
                        "The app owner needs an active Premium subscription, and "
                        "Spotify may take a few hours to re-enable requests after the status changes."
                    )
                else:
                    print(
                        "SPOTIFY: access forbidden by Spotify. "
                        "This is likely a permissions, app access, or policy restriction rather than an expired token."
                    )
            raise

    # ------------------------------------------------------------------
    # Interno: gerenciamento do cliente com TTL
    # ------------------------------------------------------------------

    def _get_client(self):
        agora = time.time()

        # Recria o cliente se ainda não existe ou se passou o TTL
        if self._client is None or agora - self._client_criado_em >= self._client_ttl:
            self._criar_cliente()

        return self._client

    def _criar_cliente(self):
        if not spotipy or not SpotifyClientCredentials:
            self._client = None
            return

        try:
            self._limpar_ambiente_oauth()
            session = self._DebugSession()
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret,
                cache_handler=MemoryCacheHandler(),
                requests_session=session,
            )
            self._client = spotipy.Spotify(
                auth_manager=auth_manager,
                requests_session=session,
            )
            self._client_criado_em = time.time()
            print("SPOTIFY: client created using ClientCredentials")
            print("SPOTIFY AUTH MANAGER:", type(self._client.auth_manager))
        except Exception as exc:
            print("SPOTIFY ERROR:", exc)
            self._client = None
            self._client_criado_em = 0

    def _invalidar_cliente(self):
        self._client = None
        self._client_criado_em = 0

    def _limpar_ambiente_oauth(self):
        os.environ.pop("SPOTIPY_REDIRECT_URI", None)
        os.environ.pop("SPOTIPY_SCOPE", None)

    # ------------------------------------------------------------------
    # Interno: cache com expiração
    # ------------------------------------------------------------------

    def _salvar_cache(self, chave, dados):
        self._cache[chave] = {
            "dados": dados,
            "expira_em": time.time() + self._cache_ttl,
        }

    # ------------------------------------------------------------------
    # Interno: parse da faixa
    # ------------------------------------------------------------------

    def _parse_track(self, faixa):
        album = faixa.get("album") or {}
        artistas = faixa.get("artists") or []
        artista = artistas[0].get("name", "") if artistas else ""
        data_lancamento = album.get("release_date", "") or ""

        return {
            "nome": faixa.get("name", "") or "",
            "artista": artista,
            "album": album.get("name", "") or "",
            "ano": data_lancamento[:4] if data_lancamento else "",
            "link_spotify": ((faixa.get("external_urls") or {}).get("spotify")) or "",
        }
