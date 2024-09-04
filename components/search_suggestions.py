import streamlit as st
import streamlit.components.v1 as components

def show_chat_input_with_suggestions(suggestions):
    # Gera o HTML das sugestões
    suggestions_html = "".join([f'<p onclick="selectSuggestion(\'{suggestion}\')">{suggestion}</p>' for suggestion in suggestions])

    # Código HTML e JavaScript para o campo de entrada de texto com sugestões
    components.html(
        f"""
        <div>
            <div id="suggestions" style="display: none; border: 1px solid #ccc; background: #fff; max-height: 150px; overflow-y: auto; position: relative; margin: 0; padding: 0;">
                <input type="text" id="search" placeholder="Search variables..." style="width: 100%; padding: 5px; box-sizing: border-box; position: sticky; top: 0; background: white;" oninput="filterSuggestions()">
                <div id="suggestions-content" style="margin: 0; padding: 0;">
                    {suggestions_html}
                </div>
            </div>
        </div>
        <script>
            const chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
            const suggestionsBox = document.getElementById('suggestions');

            // Ajuste de estilos no contêiner do iframe
            const iframeContainer = parent.document.querySelector('div[data-testid="element-container"]');
            const iframe = parent.document.querySelector('iframe[data-testid="stIFrame"]');

            // Ajusta o estilo inicial para remover margens e preenchimentos desnecessários
            iframeContainer.style.margin = '0';
            iframeContainer.style.padding = '0';
            iframeContainer.style.height = 'auto';
            iframe.style.margin = '0';
            iframe.style.padding = '0';
            iframe.style.display = 'none'; // Inicialmente, esconda o iframe

            // Mostra e esconde o iframe baseado na entrada do usuário
            chatInput.addEventListener('input', function(e) {{
                var value = e.target.value;
                if (value.includes('@')) {{
                    suggestionsBox.style.display = 'block';
                    iframe.style.display = 'block'; // Mostra o iframe
                    iframe.style.height = '100px'; // Define a altura apropriada quando exibido
                }} else {{
                    suggestionsBox.style.display = 'none';
                    iframe.style.display = 'none'; // Esconde o iframe
                    iframe.style.height = '0px'; // Garante que a altura seja 0
                }}
            }});

            chatInput.addEventListener('keyup', function(e) {{
                if (e.key === ' ') {{
                    suggestionsBox.style.display = 'none';
                    iframe.style.display = 'none'; // Esconde o iframe
                    iframe.style.height = '0px'; // Garante que a altura seja 0
                }}
            }});

            function selectSuggestion(suggestion) {{
                var chatInput = parent.document.querySelector('textarea[data-testid="stChatInputTextArea"]');
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                nativeInputValueSetter.call(chatInput, chatInput.value.replace('@', suggestion));
                var event = new Event('input', {{ bubbles: true }});
                chatInput.dispatchEvent(event);
                suggestionsBox.style.display = 'none';
                iframe.style.display = 'none'; // Esconde o iframe
                iframe.style.height = '0px'; // Garante que a altura seja 0
            }}

            function filterSuggestions() {{
                var input, filter, div, p, i;
                input = document.getElementById('search');
                filter = input.value.toUpperCase();
                div = document.getElementById('suggestions-content');
                p = div.getElementsByTagName('p');
                for (i = 0; i < p.length; i++) {{
                    txtValue = p[i].textContent || p[i].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                        p[i].style.display = "";
                    }} else {{
                        p[i].style.display = "none";
                    }}
                }}
            }}

            document.addEventListener('click', function(event) {{
                if (!suggestionsBox.contains(event.target) && !chatInput.contains(event.target)) {{
                    suggestionsBox.style.display = 'none';
                    iframe.style.display = 'none'; // Esconde o iframe
                    iframe.style.height = '0px'; // Garante que a altura seja 0
                }}
            }});
        </script>
        """,
        height=0,  
    )
