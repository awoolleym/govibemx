(function(){
  'use strict';
  var menos = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Menú móvil
  var b = document.getElementById('menuBtn'), n = document.getElementById('nav');
  if (b && n) b.addEventListener('click', function () {
    var o = n.classList.toggle('open');
    b.setAttribute('aria-expanded', o ? 'true' : 'false');
  });

  // La promo se retira sola al vencer.
  // El sitio es estático: si nadie lo regenera, la franja se queda
  // puesta con una oferta muerta. Esto la quita en cuanto pasa su
  // fecha, sin depender de que alguien se acuerde.
  var pr = document.querySelector('.promo[data-hasta]');
  if (pr) {
    var hoy = new Date();
    var h = hoy.getFullYear() + '-' +
            String(hoy.getMonth() + 1).padStart(2, '0') + '-' +
            String(hoy.getDate()).padStart(2, '0');
    if (h > pr.getAttribute('data-hasta')) pr.remove();
  }

  // Inclinación 3D de las tarjetas de servicio.
  // Antes había translateZ pero sin perspectiva en el contenedor, así
  // que no se movía nada. Ahora la rejilla tiene perspectiva y cada
  // tarjeta gira siguiendo al cursor, con 7 grados de tope.
  var tarjetas = document.querySelectorAll('.grid.g4 .card');
  if (tarjetas.length && window.matchMedia('(hover: hover)').matches
      && window.matchMedia('(min-width: 700px)').matches) {
    for (var ti = 0; ti < tarjetas.length; ti++) (function (c) {
      var pend = false;
      c.addEventListener('mousemove', function (ev) {
        if (pend) return;
        pend = true;
        requestAnimationFrame(function () {
          var r = c.getBoundingClientRect();
          var px = (ev.clientX - r.left) / r.width  - .5;
          var py = (ev.clientY - r.top)  / r.height - .5;
          c.style.setProperty('--ry', (px * 17).toFixed(2) + 'deg');
          c.style.setProperty('--rx', (-py * 17).toFixed(2) + 'deg');
          c.style.setProperty('--mx', (px * 100 + 50).toFixed(1) + '%');
          c.style.setProperty('--my', (py * 100 + 50).toFixed(1) + '%');
          pend = false;
        });
      });
      c.addEventListener('mouseleave', function () {
        c.style.setProperty('--ry', '0deg');
        c.style.setProperty('--rx', '0deg');
      });
    })(tarjetas[ti]);
  }

  // Entrar por un enlace debe dejarte arriba.
  // El navegador —y el visor de vista previa— recuerdan dónde te quedaste
  // en una página que ya habías abierto, y al volver a entrar por un
  // enlace te dejan a media altura o hasta abajo. Si la navegación es
  // nueva y no trae ancla, empezamos arriba. El botón "atrás" conserva su
  // posición, que ahí sí es lo que uno espera.
  window.addEventListener('pageshow', function (ev) {
    if (ev.persisted) return;
    var e = (window.performance && performance.getEntriesByType)
              ? performance.getEntriesByType('navigation')[0] : null;
    if (e && e.type === 'back_forward') return;
    if (location.hash) return;
    window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
  });

  if (menos) return;   // quien pidió menos movimiento, no recibe ninguno

  // A partir de aquí el JS se hace responsable de revelar. Marcamos <html>
  // para que el CSS pueda ocultar: si este script nunca corre, nada se oculta.
  document.documentElement.classList.add('anim');

  // Respaldo: pase lo que pase, a los 2.5 s todo queda visible. Más vale
  // perder la animación que perder el contenido.
  setTimeout(function () {
    var faltan = document.querySelectorAll('.reveal:not(.seen)');
    for (var i = 0; i < faltan.length; i++) faltan[i].classList.add('seen');
  }, 2500);

  // Aparición al entrar en pantalla
  var grupos = document.querySelectorAll('.js-reveal');
  for (var g = 0; g < grupos.length; g++) {
    var hijos = grupos[g].children;
    for (var i = 0; i < hijos.length; i++) {
      hijos[i].classList.add('reveal');
      if (i % 4) hijos[i].classList.add('d' + (i % 4));
    }
  }
  var secciones = document.querySelectorAll('.sec-head, .price-block, details.faq');
  for (var k = 0; k < secciones.length; k++) secciones[k].classList.add('reveal');

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('seen'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.01 });
    document.querySelectorAll('.reveal').forEach(function (el) { io.observe(el); });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) { el.classList.add('seen'); });
  }

  // Inclinación 3D de las tarjetas (solo con mouse: en táctil estorba)
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.card').forEach(function (c) {
      c.addEventListener('mousemove', function (ev) {
        var r = c.getBoundingClientRect();
        var px = (ev.clientX - r.left) / r.width - 0.5;
        var py = (ev.clientY - r.top) / r.height - 0.5;
        c.style.transform = 'perspective(850px) rotateX(' + (-py * 7).toFixed(2) +
                            'deg) rotateY(' + (px * 9).toFixed(2) + 'deg) translateY(-6px)';
        c.style.setProperty('--mx', ((ev.clientX - r.left) / r.width * 100).toFixed(1) + '%');
        c.style.setProperty('--my', ((ev.clientY - r.top) / r.height * 100).toFixed(1) + '%');
      });
      c.addEventListener('mouseleave', function () { c.style.transform = ''; });
    });
  }

  // Los números de la barra de confianza cuentan hacia arriba
  var barra = document.querySelector('.trust');
  if (barra && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (ents, ob) {
      if (!ents[0].isIntersecting) return;
      ob.disconnect();
      barra.querySelectorAll('strong').forEach(function (el) {
        var txt = el.textContent, m = txt.match(/\d+/);
        if (!m) return;
        var fin = parseInt(m[0], 10), ini = performance.now();
        (function paso(t) {
          var p = Math.min((t - ini) / 900, 1);
          var val = Math.round(fin * (1 - Math.pow(1 - p, 3)));
          el.textContent = txt.replace(/\d+/, val);
          if (p < 1) requestAnimationFrame(paso);
        })(ini);
      });
    }, { threshold: 0.4 }).observe(barra);
  }


  // ── Parallax de la foto de portada ──────────────────────────────────
  // Se mueve una fracción de lo que se mueve la página: da profundidad sin
  // marear. Se calcula dentro de requestAnimationFrame para no trabar scroll.
  var foto = document.querySelector('.hero-figure img');
  if (foto && window.innerWidth > 900) {
    var pend = false;
    window.addEventListener('scroll', function () {
      if (pend) return;
      pend = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        if (y < 900) foto.style.transform = 'translateY(' + (y * 0.07).toFixed(1) + 'px)';
        pend = false;
      });
    }, { passive: true });
  }

  // ── Portafolio: categoría + técnica ──────────────────────────────────
  var pf = document.querySelector('.pf');
  if (pf) {
    var rejilla  = pf.querySelector('.pf-rejilla');
    var piezas   = rejilla.querySelectorAll('figure');
    var pestanas = pf.querySelectorAll('.pf-tab');
    var chips    = pf.querySelectorAll('.pf-f');
    var cajasF   = pf.querySelectorAll('.pf-filtros');
    var vacio    = pf.querySelector('.pf-vacio');
    var cat = 'cabello', tec = '';

    function pinta() {
      var n = 0;
      for (var i = 0; i < piezas.length; i++) {
        var f = piezas[i];
        var ok = f.getAttribute('data-cat') === cat &&
                 (tec === '' || f.getAttribute('data-tec') === tec);
        f.hidden = !ok;
        // las piezas ocultas nunca cruzaron el observador, así que
        // entrarían en opacidad 0 y se quedarían invisibles.
        if (ok) { f.classList.add('seen'); n++; }
      }
      // Cada categoría tiene su propio juego de chips; Pestañas no tiene.
      for (var c = 0; c < cajasF.length; c++) {
        cajasF[c].hidden = (cajasF[c].getAttribute('data-cat') !== cat);
      }
      vacio.hidden = (n > 0);
    }

    // Devuelve el chip "Todo" de la categoría activa, o null si no hay chips.
    function chipTodo(c) {
      var caja = pf.querySelector('.pf-filtros[data-cat="' + c + '"]');
      return caja ? caja.querySelector('.pf-f[data-tec=""]') : null;
    }

    function transicion() {
      rejilla.classList.add('cambiando');
      setTimeout(function () {
        pinta();
        rejilla.classList.remove('cambiando');
      }, 220);
    }

    for (var a = 0; a < pestanas.length; a++) {
      (function (b) {
        b.addEventListener('click', function () {
          if (b.classList.contains('activo')) return;
          for (var j = 0; j < pestanas.length; j++) {
            pestanas[j].classList.remove('activo');
            pestanas[j].setAttribute('aria-pressed', 'false');
          }
          b.classList.add('activo'); b.setAttribute('aria-pressed', 'true');
          cat = b.getAttribute('data-cat'); tec = '';
          for (var k = 0; k < chips.length; k++) {
            var on = chips[k].getAttribute('data-tec') === '';
            chips[k].classList.toggle('activo', on);
            chips[k].setAttribute('aria-pressed', on ? 'true' : 'false');
          }
          transicion();
        });
      })(pestanas[a]);
    }

    for (var c = 0; c < chips.length; c++) {
      (function (ch) {
        ch.addEventListener('click', function () {
          if (ch.classList.contains('activo')) return;
          var hermanos = ch.parentNode.querySelectorAll('.pf-f');
          for (var j = 0; j < hermanos.length; j++) {
            hermanos[j].classList.remove('activo');
            hermanos[j].setAttribute('aria-pressed', 'false');
          }
          ch.classList.add('activo'); ch.setAttribute('aria-pressed', 'true');
          tec = ch.getAttribute('data-tec');
          transicion();
        });
      })(chips[c]);
    }

    // #cabello / #unas / #pestanas, y también las técnicas: #balayage etc.
    // Así las páginas de servicio pueden enlazar directo a su sección.
    function desdeHash() {
      var h = (location.hash || '').replace('#', '');
      if (!h) return;
      var tb = pf.querySelector('.pf-tab[data-cat="' + h + '"]');
      if (tb) { tb.click(); return; }
      var ch = pf.querySelector('.pf-f[data-tec="' + h + '"]');
      if (ch) {
        // Cada técnica vive dentro de una categoría: hay que activar la suya
        // primero o el filtro dejaría la rejilla en blanco.
        var dueno = ch.parentNode.getAttribute('data-cat');
        var tb2 = pf.querySelector('.pf-tab[data-cat="' + dueno + '"]');
        if (tb2) tb2.click();
        ch.click();
      }
    }

    pinta();
    desdeHash();
    window.addEventListener('hashchange', desdeHash);
  }

  // ── Visor de galería ────────────────────────────────────────────────
  var figs = document.querySelectorAll('.galeria figure, .pf-rejilla figure');
  if (figs.length) {
    var visor = document.createElement('div');
    visor.className = 'visor';
    visor.setAttribute('role', 'dialog');
    visor.setAttribute('aria-modal', 'true');
    visor.innerHTML = '<button class="visor-cerrar" aria-label="Cerrar">&times;</button>' +
                      '<button class="visor-nav visor-prev" aria-label="Anterior">&#8249;</button>' +
                      '<button class="visor-nav visor-next" aria-label="Siguiente">&#8250;</button>' +
                      '<figcaption></figcaption>';
    // La imagen del visor se crea con createElement y no dentro del
    // innerHTML de arriba.  Escrita ahí, la etiqueta quedaría como texto
    // literal en el código de las 21 páginas, y cualquiera que cuente
    // imágenes leyendo el HTML contaría una foto sin texto alternativo
    // que no existe: el visor está vacío hasta que alguien abre una foto,
    // y ahí sí se le copia el alt de la original (más abajo).
    var vImg = document.createElement('img');
    visor.insertBefore(vImg, visor.querySelector('figcaption'));
    document.body.appendChild(visor);
    var vCap = visor.querySelector('figcaption');
    var abridor = null;

    var vPrev = visor.querySelector('.visor-prev');
    var vNext = visor.querySelector('.visor-next');

    // Los hermanos visibles de la misma galería: en el portafolio eso
    // depende del filtro activo, así que se recalcula al abrir.
    function vecinos(fig) {
      var caja = fig.parentNode, out = [];
      var todos = caja.querySelectorAll(':scope > figure');
      for (var i = 0; i < todos.length; i++) {
        if (!todos[i].hidden) out.push(todos[i]);
      }
      return out;
    }

    function abrir(fig) {
      var im = fig.querySelector('img');
      var cap = fig.querySelector('figcaption');
      vImg.src = im.currentSrc || im.src;
      vImg.alt = im.alt || '';
      // El pie del portafolio son dos nodos (<b> y <span>); textContent los
      // pega sin espacio. Si vienen separados, los unimos con un punto medio.
      if (cap && cap.children.length > 1) {
        var trozos = [];
        for (var q = 0; q < cap.children.length; q++) {
          var tx = cap.children[q].textContent.trim();
          if (tx) trozos.push(tx);
        }
        vCap.textContent = trozos.join(' · ');
      } else {
        vCap.textContent = cap ? cap.textContent : '';
      }
      visor.classList.add('abierto');
      document.body.style.overflow = 'hidden';
      abridor = fig;
      var g = vecinos(fig);
      var solo = g.length < 2;
      vPrev.hidden = solo; vNext.hidden = solo;
      visor.querySelector('.visor-cerrar').focus();
    }

    function mover(paso) {
      if (!abridor) return;
      var g = vecinos(abridor);
      var i = g.indexOf(abridor);
      if (i < 0) return;
      abrir(g[(i + paso + g.length) % g.length]);
    }
    function cerrar() {
      visor.classList.remove('abierto');
      document.body.style.overflow = '';
      if (abridor) { abridor.focus(); abridor = null; }
    }
    for (var i = 0; i < figs.length; i++) {
      (function (fig) {
        fig.setAttribute('tabindex', '0');
        fig.setAttribute('role', 'button');
        fig.addEventListener('click', function () { abrir(fig); });
        fig.addEventListener('keydown', function (ev) {
          if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); abrir(fig); }
        });
      })(figs[i]);
    }
    visor.addEventListener('click', function (ev) {
      if (ev.target === visor || ev.target.classList.contains('visor-cerrar')) cerrar();
    });
    vPrev.addEventListener('click', function (ev) { ev.stopPropagation(); mover(-1); });
    vNext.addEventListener('click', function (ev) { ev.stopPropagation(); mover(1); });
    document.addEventListener('keydown', function (ev) {
      if (!visor.classList.contains('abierto')) return;
      if (ev.key === 'Escape') cerrar();
      else if (ev.key === 'ArrowLeft') mover(-1);
      else if (ev.key === 'ArrowRight') mover(1);
    });
    // Deslizar en celular
    var x0 = null;
    visor.addEventListener('touchstart', function (ev) {
      x0 = ev.changedTouches[0].clientX;
    }, { passive: true });
    visor.addEventListener('touchend', function (ev) {
      if (x0 === null) return;
      var d = ev.changedTouches[0].clientX - x0;
      x0 = null;
      if (Math.abs(d) > 45) mover(d < 0 ? 1 : -1);
    }, { passive: true });
  }

  // Encabezado compacto al bajar.
  // Banda muerta a propósito: entra a 88 y no sale hasta 32. Con un solo
  // umbral, el temblor normal del scroll en celular cruzaba el límite una
  // y otra vez y la clase se encendía y apagaba sin parar — medido: 7
  // cambios con 10 micro-scrolls. Eso era el parpadeo.
  var head = document.querySelector('.site-head'), ticking = false, fijo = false;
  window.addEventListener('scroll', function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      var y = window.scrollY || window.pageYOffset;
      if (!fijo && y > 88) { fijo = true; head.classList.add('scrolled'); }
      else if (fijo && y < 32) { fijo = false; head.classList.remove('scrolled'); }
      ticking = false;
    });
  }, { passive: true });

  // ── Formulario de cita ───────────────────────────────────────────────
  // Arma el mensaje y abre WhatsApp.  Nada sale hacia un servidor nuestro:
  // el sitio es estático y no hay dónde guardar.  Si esto no corre (JS
  // apagado, error antes), el action del formulario abre el chat igual.
  var fc = document.getElementById('formCita');
  if (fc) fc.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var v = function (id) {
      var el = document.getElementById(id);
      return el ? el.value.trim() : '';
    };
    var l = [fc.getAttribute('data-saludo')];
    // Los rótulos van en el mensaje para que llegue legible al teléfono
    // del salón, no como cuatro palabras sueltas.
    var campos = [['cita-nombre', 'Nombre'], ['cita-servicio', 'Servicio'],
                  ['cita-cuando', 'Cuando'], ['cita-tel', 'WhatsApp']];
    for (var i = 0; i < campos.length; i++) {
      var val = v(campos[i][0]);
      if (val) l.push(campos[i][1] + ': ' + val);
    }
    window.open('https://wa.me/525522993258?text=' +
                encodeURIComponent(l.join('\n')), '_blank', 'noopener');
  });

  // ── WebMCP ───────────────────────────────────────────────────────────
  // Las tres herramientas van declaradas en el bloque JSON de la cabecera
  // de cada página; aquí sólo se registran.  El código vive en este archivo
  // y no en el HTML porque es el mismo para las 21 páginas: puesto en la
  // cabecera eran 2.7 KB repetidos veintiuna veces, y se notó —la
  // proporción de texto contra HTML empeoró en cuatro páginas—.
  //
  // modelContext lo pone el navegador cuando trae agente.  Empezó en
  // navigator y pasó a document, así que se mira en los dos; y el método
  // bueno es registerTool, porque provideContext salió de la
  // especificación en marzo de 2026.
  var decl = document.getElementById('webmcp-tools');
  var mc = document.modelContext || navigator.modelContext;
  if (decl && mc) {
    var tools = null;
    try { tools = JSON.parse(decl.textContent); } catch (e) { tools = null; }
    var acciones = {
      book_appointment: function (args) {
        var f = document.getElementById('formCita');
        // El formulario sólo existe en la portada.  Desde cualquier otra
        // página la acción lleva hasta él en vez de fallar en silencio.
        if (!f) {
          location.href = (document.documentElement.lang === 'en' ? '/en/' : '/') + '#contacto';
          return { content: [{ type: 'text', text: 'Abriendo el formulario de cita.' }] };
        }
        var a = args || {};
        ['nombre', 'tel', 'servicio', 'cuando'].forEach(function (k) {
          var el = document.getElementById('cita-' + k);
          if (el && a[k]) el.value = a[k];
        });
        f.requestSubmit ? f.requestSubmit() : f.submit();
        return { content: [{ type: 'text',
                 text: 'Cita enviada por WhatsApp a Stilo Salon.' }] };
      },
      get_prices: function () {
        return { content: [{ type: 'text', text: 'https://stilo-salon.com/llms.txt' }] };
      },
      get_location_and_hours: function () {
        return { content: [{ type: 'text',
                 text: 'Calle Guadalajara 70-B, Roma Norte, Cuauhtémoc, 06700, Ciudad de México. ' +
                       'Lunes a viernes 9:00-20:00, sabado 9:00-19:00, domingo cerrado. ' +
                       'Tel 55 2299 3258.' }] };
      }
    };
    var completa = function (t) {
      return { name: t.name, description: t.description,
               inputSchema: t.inputSchema, execute: acciones[t.name] };
    };
    try {
      if (tools && typeof mc.registerTool === 'function') {
        tools.forEach(function (t) { mc.registerTool(completa(t)); });
      } else if (tools && typeof mc.provideContext === 'function') {
        mc.provideContext({ tools: tools.map(completa) });
      }
    } catch (err) { /* si la API cambia otra vez, la página no se cae */ }
  }
})();
