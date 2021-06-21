messages = {
    'hello_msg': 
"""
Olá, sou Tinder Brazil 🇧🇷, me adicione ao seu chat e me dê direitos de administrador.

Quais comandos eu conheço?

/stat -> Obtenha estatísticas e configurações.
/ban (Deve ser responder a mensagem) -> Banir membro.
/mute (Deve responder à mensagem) -> Silenciar membro.
/warn -> Avisar membro.
/unban -> Desbanir membro.
/unmute -> Membro com som.
/status (Deve ser responder à mensagem) -> Obter informações sobre o membro.
/ws -> Habilitar / desabilitar/ Sistema de proteção contra spam.
/setbantime -> Defina um tempo de proibição específico, defina zero para desativá-lo.
/setwarnstoban -> Defina uma contagem específica de avisos para banir.

""",
    'stat_msg': 
"""Total de mensagens: {ttl_msg}
Avisos para banir: {w_to_ban}
Sistema de Boas Vindas: {ws}
Tempo: {tm_ban} seconds
Top de membros por atividade"
""",

'member_info': 
"""User:Sistema de boas-vindas: {full_name}
Mensagens deste usuário: {member_msg_count}
Reputação: {mem_rep}
Avisos: {warns}/{warns_to_ban}
""",

"enabled": "ativado",
"disabled": "Desativado",
"ws_edit": "{name} {action} sistema de boas-vindas.",
"msg_ch_bantime": "{name} mudou bantime para {new}.",
"invalid_arg": "Erro, argumento inválido fornecido.",

}

def get_message(message_type):
    """
    Apenas um invólucro bonito.
    Returns messages[message_type]
    """

    try:
        return messages[message_type]
    except KeyError:
        raise ValueError(f"Invalid message type: {message_type}")
