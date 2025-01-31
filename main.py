import streamlit as st
from streamlit_keyup import keyup
import random
import time


def init_game_state():
    """Inicializa o estado do jogo se ainda não existir"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'player_position': 0,            # Posição horizontal do jogador
            # Pista atual (0: superior, 1: meio, 2: inferior)
            'player_lane': 1,
            'track_length': 40,              # Comprimento da pista
            'game_over': False,
            'obstacles': [],                 # Lista de obstáculos
            'score': 0,                      # Pontuação atual
            'high_score': 0,                 # Recorde
            'player_speed': 2,               # Velocidade atual
            'max_speed': 5,                  # Velocidade máxima
            'lives': 3,                      # Vidas restantes
            'boost_available': True,         # Se o turbo está disponível
            'last_key': None                 # Última tecla pressionada
        }
        # Gera obstáculos iniciais
        st.session_state.game_state['obstacles'] = generate_obstacles()


def handle_input():
    """Processa input do teclado"""
    key = keyup(label="game", key="keyboard")

    if key:
        # Evita processamento duplicado da mesma tecla
        if key != st.session_state.game_state['last_key']:
            st.session_state.game_state['last_key'] = key

            # Controles
            if key == "ArrowUp":
                move_up()
            elif key == "ArrowDown":
                move_down()
            elif key == "ArrowRight":
                accelerate()
            elif key == "ArrowLeft":
                brake()
            elif key == " ":  # Tecla espaço
                use_boost()
            elif key == "r":  # Tecla R
                reset_game()


def generate_obstacles():
    """Gera novos obstáculos para a pista"""
    track_length = st.session_state.game_state['track_length']
    return [
        {'lane': 0, 'position': random.randint(25, track_length - 5)},
        {'lane': 1, 'position': random.randint(25, track_length - 5)},
        {'lane': 2, 'position': random.randint(25, track_length - 5)}
    ]


def move_up():
    """Move o jogador para a pista superior"""
    if st.session_state.game_state['player_lane'] > 0:
        st.session_state.game_state['player_lane'] -= 1
        st.session_state.game_state['player_speed'] = max(
            1, st.session_state.game_state['player_speed'] - 0.5)


def move_down():
    """Move o jogador para a pista inferior"""
    if st.session_state.game_state['player_lane'] < 2:
        st.session_state.game_state['player_lane'] += 1
        st.session_state.game_state['player_speed'] = max(
            1, st.session_state.game_state['player_speed'] - 0.5)


def accelerate():
    """Aumenta a velocidade do jogador"""
    if st.session_state.game_state['player_speed'] < st.session_state.game_state['max_speed']:
        st.session_state.game_state['player_speed'] += 0.5


def brake():
    """Reduz a velocidade do jogador"""
    if st.session_state.game_state['player_speed'] > 1:
        st.session_state.game_state['player_speed'] -= 0.5


def use_boost():
    """Ativa o turbo"""
    if st.session_state.game_state['boost_available']:
        st.session_state.game_state['player_speed'] = min(
            st.session_state.game_state['player_speed'] + 2,
            st.session_state.game_state['max_speed']
        )
        st.session_state.game_state['boost_available'] = False


def check_collision():
    """Verifica se houve colisão com obstáculos"""
    player_lane = st.session_state.game_state['player_lane']
    player_pos = st.session_state.game_state['player_position']

    for obstacle in st.session_state.game_state['obstacles']:
        if (obstacle['lane'] == player_lane and
                abs(player_pos - obstacle['position']) < 2):
            return True
    return False


def move_player():
    """Atualiza a posição do jogador e verifica colisões"""
    if not st.session_state.game_state['game_over']:
        # Move o jogador
        st.session_state.game_state['player_position'] += st.session_state.game_state['player_speed']

        # Verifica colisão
        if check_collision():
            st.session_state.game_state['lives'] -= 1
            st.session_state.game_state['player_speed'] = 2
            if st.session_state.game_state['lives'] <= 0:
                st.session_state.game_state['game_over'] = True
                if st.session_state.game_state['score'] > st.session_state.game_state['high_score']:
                    st.session_state.game_state['high_score'] = st.session_state.game_state['score']
            else:
                # Recua o jogador após colisão
                st.session_state.game_state['player_position'] = max(
                    0, st.session_state.game_state['player_position'] - 10)

        # Verifica se completou a pista
        if st.session_state.game_state['player_position'] >= st.session_state.game_state['track_length']:
            st.session_state.game_state['player_position'] = 0
            st.session_state.game_state['score'] += int(
                100 * st.session_state.game_state['player_speed'])
            st.session_state.game_state['obstacles'] = generate_obstacles()
            st.session_state.game_state['boost_available'] = True


def render_track():
    """Renderiza o estado atual da pista"""
    tracks = []
    player_pos = int(st.session_state.game_state['player_position'])

    # Renderiza cada pista
    for lane in range(3):
        track = ['═'] * st.session_state.game_state['track_length']

        # Adiciona obstáculo
        for obstacle in st.session_state.game_state['obstacles']:
            if obstacle['lane'] == lane:
                pos = int(obstacle['position'])
                if 0 <= pos < len(track):
                    track[pos] = '🌲'

        # Adiciona jogador
        if lane == st.session_state.game_state['player_lane'] and 0 <= player_pos < len(track):
            track[player_pos] = '🏎️'

        # Adiciona bordas e número da pista
        track_str = f"{lane + 1} ║{''.join(track)}║"
        tracks.append(track_str)

    # Adiciona uma linha de meta
    finish_line = "  " + "╠" + "═" * \
        st.session_state.game_state['track_length'] + "╣"

    return "\n".join(tracks + [finish_line])


def reset_game():
    """Reinicia o estado do jogo"""
    st.session_state.game_state['player_position'] = 0
    st.session_state.game_state['player_lane'] = 1
    st.session_state.game_state['game_over'] = False
    st.session_state.game_state['obstacles'] = generate_obstacles()
    st.session_state.game_state['score'] = 0
    st.session_state.game_state['player_speed'] = 2
    st.session_state.game_state['lives'] = 3
    st.session_state.game_state['boost_available'] = True
    st.session_state.game_state['last_key'] = None


def main():
    st.set_page_config(page_title="Corrida Maluca", layout="centered")

    # Inicializa o estado do jogo
    init_game_state()

    st.title('🏁 Corrida Maluca 🏁')

    # Instruções do jogo
    with st.expander("📖 Como Jogar"):
        st.write("""
        Controles do Teclado:
        - ⬆️ Seta para cima: Subir de pista
        - ⬇️ Seta para baixo: Descer de pista
        - ➡️ Seta para direita: Acelerar
        - ⬅️ Seta para esquerda: Frear
        - Barra de Espaço: Usar Turbo
        - Tecla R: Reiniciar jogo
        
        Objetivo:
        1. Desvie dos obstáculos (🌲)
        2. Complete voltas para ganhar pontos
        3. Use o turbo (🚀) para ganhar velocidade extra
        4. Cuidado: você perde uma vida ao bater!
        """)

    # Processa input do teclado
    handle_input()

    # Status do jogo
    st.subheader("📊 Status")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("❤️ Vidas", st.session_state.game_state['lives'])
    with col2:
        st.metric("🏃 Velocidade", f"{
                  st.session_state.game_state['player_speed']:.1f}")
    with col3:
        st.metric("🎯 Pontuação", st.session_state.game_state['score'])
    with col4:
        st.metric("🏆 Recorde", st.session_state.game_state['high_score'])

    # Pista
    st.subheader("🛣️ Pista")
    st.code(render_track(), language=None)

    # Controles alternativos (botões)
    st.subheader("🎮 Controles Alternativos")

    # Movimento
    col1, col2 = st.columns(2)
    with col1:
        if st.button('⬆️ Subir'):
            move_up()
    with col2:
        if st.button('⬇️ Descer'):
            move_down()

    # Velocidade
    col1, col2 = st.columns(2)
    with col1:
        if st.button('➡️ Acelerar'):
            accelerate()
    with col2:
        if st.button('⬅️ Frear'):
            brake()

    # Turbo e Reset
    col1, col2 = st.columns(2)
    with col1:
        if st.button('🚀 Turbo', disabled=not st.session_state.game_state['boost_available']):
            use_boost()
    with col2:
        if st.button('🔄 Reiniciar'):
            reset_game()

    # Atualiza estado do jogo
    move_player()

    # Game Over
    if st.session_state.game_state['game_over']:
        st.error('🔥 Game Over! 🔥')
        st.button('🎮 Jogar Novamente', on_click=reset_game)

    # Atualiza a página
    time.sleep(0.1)
    st.rerun()


if __name__ == '__main__':
    main()
