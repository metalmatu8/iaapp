"""
llm_integration.py - Integración con modelos LLM (OpenAI, Ollama)
Soporta generación de respuestas personalizadas basadas en propiedades recuperadas
"""

import os
from config import LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL

class LLMProvider:
    """Interfaz abstracta para proveedores LLM"""
    
    def generar_respuesta(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """Proveedor OpenAI GPT-4o/mini"""
    
    def __init__(self):
        try:
            import openai
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        except ImportError:
            raise ImportError("openai no está instalado. Instala con: pip install openai")
    
    def generar_respuesta(self, prompt: str) -> str:
        """Genera respuesta usando OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al generar respuesta con OpenAI: {str(e)}"


class OllamaProvider(LLMProvider):
    """Proveedor Ollama (modelos locales: Llama 3, Mistral, etc.)"""
    
    def __init__(self):
        try:
            import requests
            self.requests = requests
            self.base_url = OLLAMA_BASE_URL
            # Verificar conectividad
            try:
                response = self.requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    raise ConnectionError(f"Ollama no responde en {self.base_url}")
            except Exception as e:
                raise ConnectionError(f"No se puede conectar a Ollama en {self.base_url}: {str(e)}")
        except ImportError:
            raise ImportError("requests no está instalado. Instala con: pip install requests")
    
    def generar_respuesta(self, prompt: str) -> str:
        """Genera respuesta usando Ollama local"""
        try:
            response = self.requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json().get("response", "Sin respuesta")
            else:
                return f"Error Ollama: {response.status_code}"
        except Exception as e:
            return f"Error al generar respuesta con Ollama: {str(e)}"


class MockProvider(LLMProvider):
    """Proveedor Mock para testing (no requiere APIs)"""
    
    def generar_respuesta(self, prompt: str) -> str:
        return "Esta es una respuesta de demostración. Para usar un LLM real, configura OPENAI_API_KEY o instala Ollama."


def obtener_llm_provider() -> LLMProvider:
    """Factory para obtener el proveedor LLM configurado"""
    
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada")
        return OpenAIProvider()
    
    elif LLM_PROVIDER == "ollama":
        return OllamaProvider()
    
    elif LLM_PROVIDER == "ninguno":
        return MockProvider()
    
    else:
        raise ValueError(f"LLM_PROVIDER inválido: {LLM_PROVIDER}. Opciones: 'openai', 'ollama', 'ninguno'")


def generar_recomendacion(llm: LLMProvider, perfil_usuario: str, propiedades: list) -> str:
    """
    Genera una recomendación personalizada para el usuario basada en propiedades recuperadas.
    
    Args:
        llm: Proveedor LLM
        perfil_usuario: Descripción de preferencias del usuario
        propiedades: Lista de propiedades recuperadas (dicts con id, tipo, zona, precio, etc.)
    
    Returns:
        Respuesta generada por el LLM
    """
    
    # Formatear contexto de propiedades
    context = ""
    for i, prop in enumerate(propiedades, 1):
        context += f"\n{i}. {prop['tipo']} en {prop['zona']}\n"
        context += f"   - Precio: USD {prop['precio']}\n"
        context += f"   - Habitaciones: {prop['habitaciones']}, Baños: {prop['baños']}\n"
        context += f"   - M² cubiertos: {prop['metros_cubiertos']}, M² descubiertos: {prop['metros_descubiertos']}\n"
        context += f"   - Pileta: {'Sí' if prop['pileta'] else 'No'}\n"
        context += f"   - Descripción: {prop['descripcion']}\n"
        context += f"   - Amenities: {prop['amenities']}\n"
    
    # Prompt personalizado
    prompt = f"""Perfil del usuario: {perfil_usuario}

Propiedades encontradas:
{context}

Por favor, explica por qué estas propiedades son adecuadas para el usuario, destacando las características que coinciden con sus preferencias. Sé conciso y amigable."""
    
    return llm.generar_respuesta(prompt)
