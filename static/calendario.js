document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.calendar-table td.day').forEach(cell => {
        cell.addEventListener('click', () => {
            const fecha = cell.dataset.date;
            fetch(`/perfil/calendario/dia?date=${fecha}`)
                .then(r => r.json())
                .then(data => showDetalle(data));
        });
    });

    document.getElementById('cerrar-detalle').addEventListener('click', () => {
        document.getElementById('detalle-dia').style.display = 'none';
    });
});

function showDetalle(data) {
    const modal = document.getElementById('detalle-dia');
    const fechaEl = document.getElementById('detalle-fecha');
    const lista = document.getElementById('detalle-eventos');
    const inputFecha = document.getElementById('input-fecha');
    fechaEl.textContent = data.date;
    inputFecha.value = data.date;
    lista.innerHTML = '';
    if (data.eventos && data.eventos.length) {
        data.eventos.forEach(e => {
            const li = document.createElement('li');
            li.textContent = e.titulo + (e.descripcion ? ': ' + e.descripcion : '');
            lista.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No hay eventos para este día';
        lista.appendChild(li);
    }
    modal.style.display = 'block';
}
