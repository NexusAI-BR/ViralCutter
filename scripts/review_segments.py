"""
Agente Revisor de Qualidade de Cortes Virais.
Avalia cada segmento candidato para garantir coerência narrativa,
compreensão independente e potencial viral.
"""
import json
import re
import time


REVIEW_PROMPT_TEMPLATE = """Você é um Revisor de Qualidade de Conteúdo Viral especialista.

Sua tarefa é avaliar se um trecho de transcrição funciona como um vídeo viral INDEPENDENTE (TikTok/Reels/Shorts).

### TRECHO PARA AVALIAÇÃO:
{segment_text}

### CRITÉRIOS DE AVALIAÇÃO (avalie cada um de 0 a 100):

1. **HOOK (Início):** O trecho começa com algo que prende atenção imediatamente? Tem um gancho forte nos primeiros 3-5 segundos?
2. **DESENVOLVIMENTO (Meio):** A história se desenvolve com detalhes, tensão, humor ou valor? Mantém o interesse?
3. **CONCLUSÃO (Fim):** O trecho termina de forma satisfatória? Tem uma conclusão, punchline ou lição? Ou corta no meio de uma frase/ideia?
4. **INDEPENDÊNCIA:** Alguém que NUNCA assistiu o vídeo original consegue entender o trecho do zero? Há referências sem contexto ("ele", "aquilo", "esse cara" sem apresentação)?
5. **VIRALIDADE:** O conteúdo tem potencial para ser compartilhado? É surpreendente, engraçado, emotivo, polêmico ou educativo?

### REGRAS:
- Se o trecho começa no meio de uma conversa sem contexto → nota 0 em INDEPENDÊNCIA
- Se o trecho termina com frase cortada ou "e aí..." → nota 0 em CONCLUSÃO
- Se o trecho é genérico e sem valor → nota baixa em VIRALIDADE

### FORMATO DE RESPOSTA (JSON APENAS):
{{
    "hook_score": 0-100,
    "development_score": 0-100,
    "conclusion_score": 0-100,
    "independence_score": 0-100,
    "virality_score": 0-100,
    "overall_score": 0-100,
    "approved": true/false,
    "reason": "Explicação breve do motivo da aprovação ou reprovação",
    "suggestion": "Se reprovado, sugestão de como melhorar (expandir início, expandir fim, etc)"
}}

Responda APENAS com JSON válido. Sem markdown, sem comentários.
"""


def _extract_segment_text(transcript_segments, start_time, end_time):
    """Extrai o texto completo de um segmento a partir da transcrição."""
    texts = []
    for seg in transcript_segments:
        seg_start = seg.get('start', 0)
        seg_end = seg.get('end', 0)
        # Se há sobreposição com o intervalo do segmento
        if seg_end > start_time and seg_start < end_time:
            texts.append(seg.get('text', '').strip())
    return ' '.join(texts)


def _call_ai_for_review(prompt, ai_mode, api_key, model_name):
    """Envia o prompt de revisão para a IA."""
    if ai_mode == "gemini":
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)
            
            max_retries = 3
            base_wait = 15
            
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "Quota exceeded" in error_str:
                        wait_time = base_wait * (attempt + 1)
                        match = re.search(r"retry in (\d+(\.\d+)?)s", error_str)
                        if match:
                            wait_time = float(match.group(1)) + 5.0
                        print(f"  [429] Quota. Aguardando {wait_time:.0f}s (tentativa {attempt+1}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  [ERRO] Revisão Gemini: {e}")
                        return None
            print("  [ERRO] Max retries atingido na revisão.")
            return None
            
        except ImportError:
            print("  [ERRO] google-generativeai não disponível para revisão.")
            return None
            
    elif ai_mode == "g4f":
        try:
            import g4f
            response = g4f.ChatCompletion.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            if isinstance(response, str):
                return response
            elif isinstance(response, dict):
                if 'choices' in response:
                    return response['choices'][0].get('message', {}).get('content', '')
                return json.dumps(response)
            return str(response)
        except Exception as e:
            print(f"  [ERRO] Revisão G4F: {e}")
            return None
    
    return None


def _parse_review_response(response_text):
    """Parseia a resposta JSON da revisão."""
    if not response_text:
        return None
    
    # Limpa markdown code blocks
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    
    try:
        # Tenta parse direto
        data = json.loads(response_text.strip())
        return data
    except json.JSONDecodeError:
        pass
    
    # Tenta encontrar JSON no texto
    try:
        match = re.search(r'\{[^{}]*"overall_score"[^{}]*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    
    # Tenta raw_decode
    try:
        decoder = json.JSONDecoder()
        # Encontra o primeiro '{'
        start = response_text.find('{')
        if start != -1:
            obj, _ = decoder.raw_decode(response_text[start:])
            if 'overall_score' in obj:
                return obj
    except:
        pass
    
    return None


def review_and_refine(segments_data, transcript_segments, ai_mode, api_key, model_name, 
                      min_duration, max_duration, min_score=70):
    """
    Revisa cada segmento candidato usando IA para avaliar qualidade narrativa.
    
    Args:
        segments_data: dict com chave 'segments' contendo lista de segmentos
        transcript_segments: lista de segmentos da transcrição (com start/end/text)
        ai_mode: 'gemini' ou 'g4f'
        api_key: API key (para gemini)
        model_name: nome do modelo
        min_duration: duração mínima
        max_duration: duração máxima
        min_score: score mínimo para aprovação (default: 70)
    
    Returns:
        dict com 'segments' filtrados e revisados
    """
    if ai_mode not in ("gemini", "g4f"):
        print("[REVISOR] Revisão disponível apenas para backends Gemini e G4F. Pulando revisão.")
        return segments_data
    
    segments = segments_data.get("segments", [])
    if not segments:
        return segments_data
    
    print(f"\n{'='*60}")
    print(f"  AGENTE REVISOR DE QUALIDADE - Avaliando {len(segments)} segmentos")
    print(f"{'='*60}")
    
    approved_segments = []
    
    for i, segment in enumerate(segments):
        title = segment.get('title', f'Segmento {i+1}')
        start_time = segment.get('start_time', 0)
        end_time = segment.get('end_time', 0)
        duration = segment.get('duration', end_time - start_time)
        
        print(f"\n[{i+1}/{len(segments)}] Revisando: \"{title}\" ({duration:.1f}s)")
        
        # Extrair texto real do segmento
        segment_text = _extract_segment_text(transcript_segments, start_time, end_time)
        
        if not segment_text or len(segment_text.strip()) < 20:
            print(f"  ✗ Texto muito curto ou vazio. Reprovado.")
            continue
        
        # Montar prompt de revisão
        review_prompt = REVIEW_PROMPT_TEMPLATE.format(segment_text=segment_text)
        
        # Chamar IA
        response_text = _call_ai_for_review(review_prompt, ai_mode, api_key, model_name)
        
        if not response_text:
            print(f"  ⚠ Falha na revisão (sem resposta da IA). Mantendo segmento por precaução.")
            approved_segments.append(segment)
            continue
        
        # Parsear resposta
        review = _parse_review_response(response_text)
        
        if not review:
            print(f"  ⚠ Falha ao parsear resposta da revisão. Mantendo segmento.")
            approved_segments.append(segment)
            continue
        
        overall_score = review.get('overall_score', 0)
        is_approved = review.get('approved', overall_score >= min_score)
        reason = review.get('reason', 'N/A')
        suggestion = review.get('suggestion', '')
        
        # Detalhar scores
        hook = review.get('hook_score', '?')
        dev = review.get('development_score', '?')
        conclusion = review.get('conclusion_score', '?')
        independence = review.get('independence_score', '?')
        virality = review.get('virality_score', '?')
        
        print(f"  Scores: Hook={hook} | Dev={dev} | Conclusão={conclusion} | Indep={independence} | Viral={virality}")
        print(f"  Score Geral: {overall_score}/100")
        print(f"  Motivo: {reason}")
        
        if is_approved and overall_score >= min_score:
            print(f"  ✓ APROVADO (score: {overall_score})")
            # Atualizar score do segmento com o score da revisão
            segment['review_score'] = overall_score
            segment['review_reason'] = reason
            # Usar o maior score entre o original e o da revisão
            original_score = segment.get('score', 0)
            try:
                segment['score'] = int((int(original_score) + overall_score) / 2)
            except (ValueError, TypeError):
                segment['score'] = overall_score
            approved_segments.append(segment)
        else:
            print(f"  ✗ REPROVADO (score: {overall_score})")
            if suggestion:
                print(f"  Sugestão: {suggestion}")
        
        # Espera entre chamadas para respeitar rate limits
        if i < len(segments) - 1:
            time.sleep(2)
    
    print(f"\n{'='*60}")
    print(f"  RESULTADO: {len(approved_segments)}/{len(segments)} segmentos aprovados")
    print(f"{'='*60}\n")
    
    # Re-ordenar por score
    approved_segments.sort(key=lambda x: int(x.get('score', 0)), reverse=True)
    
    return {"segments": approved_segments}
