function mostrarImagem(img) {
    const overlay = document.getElementById('overlay');
    const imagemExpandida = document.getElementById('imagemExpandida');
    imagemExpandida.src = img.src;
    overlay.style.display = 'flex';
}

function fecharImagem() {
    document.getElementById('overlay').style.display = 'none';
}


function abrirFormulario(id) {
    const form = document.getElementById(`formulario-${id}`);
    if (form) {
        form.style.display = 'block';
    }
}

function fecharFormulario(id) {
    const form = document.getElementById(`formulario-${id}`);
    if (form) {
        form.style.display = 'none';
    } else {
        console.warn(`Formulário com ID formulario-${id} não encontrado`);
    }
}

function abrirFormularioManutencao(tipo, id) {
    const form = document.getElementById(`form-manutencao-${tipo}-${id}`);
    if (form) form.style.display = 'block';
}

function fecharFormularioManutencao(tipo, id) {
    const form = document.getElementById(`form-manutencao-${tipo}-${id}`);
    if (form) form.style.display = 'none';
}


