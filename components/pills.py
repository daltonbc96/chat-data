from streamlit_pills import pills
from typing import Iterable, Union, Callable
import streamlit as st

def custom_pills(label: str, options: dict, icons: Iterable[str] = None, index: Union[int, None] = 0,
                 format_func: Callable = None, label_visibility: str = "visible", clearable: bool = None,
                 key: str = None, reset_key: str = None):
    """
    Mostra pills clicáveis com a opção de resetar a seleção.

    Args:
        label (str): O rótulo mostrado acima das pills.
        options (dict): Um dicionário onde as chaves são textos curtos das pills e os valores são textos elaborados.
        icons (iterable of str, optional): Os ícones de emoji mostrados no lado esquerdo das pills. Cada item deve ser um único emoji. Padrão None.
        index (int or None, optional): O índice da pill que é selecionada por padrão. Se None, nenhuma pill é selecionada. Padrão 0.
        format_func (callable, optional): Uma função que é aplicada ao texto da pill antes da renderização. Padrão None.
        label_visibility ("visible" or "hidden" or "collapsed", optional): A visibilidade do rótulo. Use isso em vez de `label=""` para acessibilidade. Padrão "visible".
        clearable (bool, optional): Se o usuário pode desmarcar a pill selecionada clicando nela. Padrão None.
        key (str, optional): A chave do componente. Padrão None.
        reset_key (str, optional): A chave utilizada para resetar a seleção. Padrão None.

    Returns:
        (any): O texto elaborado da pill selecionada pelo usuário (valor em `options`).
    """
    
    # Crie uma chave única para o componente para forçar a atualização quando necessário
    unique_key = f"{key}-{reset_key}" if key and reset_key else key

    # Extraia os textos curtos para mostrar como opções
    short_texts = list(options.keys())

    st.write("Prompt Suggestions")

    # Passar os argumentos para a função pills
    selected_short_text = pills(label=label, options=short_texts, icons=icons, index=index, format_func=format_func,
                                label_visibility=label_visibility, clearable=clearable, key=unique_key)
    
    # Retorne o texto elaborado correspondente ao texto curto selecionado
    return options.get(selected_short_text)
