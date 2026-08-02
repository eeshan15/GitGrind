/* ==========================================================================
   Subnetting and CIDR.

   Everything here is one idea: the prefix length cuts the 32 bits into a network
   part and a host part. So the binary is shown first, split at exactly that
   point, and every derived number - mask, network, broadcast, usable range,
   host count - is read off that split rather than computed by a separate rule.

   Borrowing bits to make subnets is the same cut moved further right, which the
   subnet list makes visible.
   ========================================================================== */
(function () {
  const { el } = GG;

  const toInt = ip => {
    const p = String(ip || '').trim().split('.');
    if (p.length !== 4) throw new Error('An address looks like 192.168.10.0');
    return p.reduce((a, o) => {
      const n = Number(o);
      if (!/^\d+$/.test(o) || n < 0 || n > 255) throw new Error('"' + o + '" is not 0-255.');
      return ((a << 8) >>> 0) + n;
    }, 0) >>> 0;
  };
  const toDots = n => [24, 16, 8, 0].map(s => (n >>> s) & 255).join('.');
  const toBits = n => [24, 16, 8, 0].map(s => {
    let b = ((n >>> s) & 255).toString(2);
    while (b.length < 8) b = '0' + b;
    return b;
  }).join('.');

  function simulate(values) {
    const ip = toInt(values.address);
    const prefix = Math.max(0, Math.min(32, values.prefix | 0));
    const borrow = Math.max(0, Math.min(32 - prefix, values.borrow | 0));

    const mask = prefix === 0 ? 0 : (0xFFFFFFFF << (32 - prefix)) >>> 0;
    const network = (ip & mask) >>> 0;
    const broadcast = (network | (~mask >>> 0)) >>> 0;
    const hostBits = 32 - prefix;
    const total = Math.pow(2, hostBits);
    const usable = hostBits <= 1 ? total : total - 2;

    const out = [];
    const base = { ip, prefix, mask, network, broadcast, hostBits, total, usable,
                   borrow, subnets: [] };

    out.push(Object.assign({}, base, {
      caption: 'The address in binary. A /' + prefix + ' means the first ' + prefix +
               ' bits identify the network and the remaining ' + hostBits +
               ' bits identify a host inside it. Everything else follows from that cut.',
    }));

    out.push(Object.assign({}, base, {
      caption: 'Mask ' + toDots(mask) + ' is just ' + prefix + ' ones followed by ' +
               hostBits + ' zeros. ANDing the address with it clears the host bits, ' +
               'which gives the network address ' + toDots(network) + '.',
    }));

    out.push(Object.assign({}, base, {
      caption: 'Setting every host bit to 1 instead gives the broadcast address ' +
               toDots(broadcast) + '. So the block runs ' + toDots(network) + ' to ' +
               toDots(broadcast) + '.',
    }));

    out.push(Object.assign({}, base, {
      caption: hostBits <= 1
        ? 'With ' + hostBits + ' host bit(s) there are ' + total + ' address(es) and no ' +
          'network/broadcast pair to subtract - a /31 is used for point-to-point links.'
        : '2^' + hostBits + ' = ' + total + ' addresses in total. The network address ' +
          'and the broadcast address are not assignable, so ' + usable +
          ' host(s) can actually be configured.',
    }));

    if (borrow > 0) {
      const newPrefix = prefix + borrow;
      const count = Math.pow(2, borrow);
      const size = Math.pow(2, 32 - newPrefix);
      const newMask = (0xFFFFFFFF << (32 - newPrefix)) >>> 0;
      const subnets = [];
      for (let i = 0; i < Math.min(count, 32); i++) {
        const net = (network + i * size) >>> 0;
        subnets.push({
          i, net, bcast: (net + size - 1) >>> 0,
          first: (net + 1) >>> 0, last: (net + size - 2) >>> 0,
          size, usable: size <= 2 ? size : size - 2,
        });
      }
      out.push(Object.assign({}, base, {
        prefix: newPrefix, mask: newMask, subnets, count, size,
        caption: 'Borrowing ' + borrow + ' host bit(s) moves the cut right, to /' +
                 newPrefix + '. That makes 2^' + borrow + ' = ' + count +
                 ' subnet(s) of ' + size + ' address(es) each, ' +
                 (size <= 2 ? size : size - 2) + ' of them usable.' +
                 (count > 32 ? ' Only the first 32 are listed.' : ''),
      }));
    }

    out.push(Object.assign({}, base, {
      subnets: out.length && out[out.length - 1].subnets || [],
      prefix: borrow ? prefix + borrow : prefix,
      mask: borrow ? (0xFFFFFFFF << (32 - prefix - borrow)) >>> 0 : mask,
      caption: 'Summary: ' + toDots(network) + '/' + prefix + ', mask ' + toDots(mask) +
               ', range ' + toDots(network) + ' - ' + toDots(broadcast) + ', ' +
               usable + ' usable host(s)' +
               (borrow ? ', split into ' + Math.pow(2, borrow) + ' subnet(s).' : '.'),
    }));
    return out;
  }

  /* ------------------------------------------------------------- drawing -- */
  function draw(host, frame) {
    /* the 32 bits, cut at the prefix */
    const bits = toBits(frame.ip).replace(/\./g, '');
    const strip = el('div', { class: 'viz-bits' });
    for (let i = 0; i < 32; i++) {
      strip.appendChild(el('span', {
        class: 'viz-bit' + (i < frame.prefix ? ' net' : ' hostb') +
               (i === frame.prefix - 1 ? ' edge' : '') +
               ((i + 1) % 8 === 0 && i !== 31 ? ' octet' : ''),
        text: bits[i],
      }));
    }
    host.appendChild(strip);
    host.appendChild(el('div', { class: 'viz-bitkey' }, [
      el('span', { class: 'k net', text: 'network (' + frame.prefix + ' bits)' }),
      el('span', { class: 'k hostb', text: 'host (' + (32 - frame.prefix) + ' bits)' }),
    ]));

    const rows = [
      ['address', toDots(frame.ip)],
      ['mask', toDots(frame.mask) + '  /' + frame.prefix],
      ['network', toDots(frame.network)],
      ['broadcast', toDots(frame.broadcast)],
      ['first host', frame.hostBits > 1 ? toDots(frame.network + 1) : '-'],
      ['last host', frame.hostBits > 1 ? toDots(frame.broadcast - 1) : '-'],
      ['usable hosts', String(frame.usable)],
    ];
    const table = el('div', { class: 'viz-results' });
    rows.forEach(([k, v]) => table.appendChild(el('div', { class: 'viz-rrow' }, [
      el('span', { text: k }), el('span', { text: v }),
    ])));
    host.appendChild(table);

    if (frame.subnets && frame.subnets.length) {
      const sub = el('div', { class: 'viz-results', style: 'margin-top:14px' });
      sub.appendChild(el('div', { class: 'viz-rrow head' }, [
        el('span', { text: '#' }), el('span', { text: 'network' }),
        el('span', { text: 'first' }), el('span', { text: 'last' }),
        el('span', { text: 'broadcast' }), el('span', { text: 'hosts' }),
      ]));
      frame.subnets.forEach(s => sub.appendChild(el('div', { class: 'viz-rrow' }, [
        el('span', { text: String(s.i) }),
        el('span', { text: toDots(s.net) }),
        el('span', { text: s.size > 2 ? toDots(s.first) : '-' }),
        el('span', { text: s.size > 2 ? toDots(s.last) : '-' }),
        el('span', { text: toDots(s.bcast) }),
        el('span', { text: String(s.usable) }),
      ])));
      host.appendChild(sub);
    }
  }

  GG.viz.register('cn-subnet', {
    title: 'Subnetting and CIDR',
    subtitle: 'Watch the prefix cut the 32 bits in two, then read the mask, network, ' +
              'broadcast and host range straight off that cut.',
    glyph: 'N',
    topic: 'ip-addressing',
    note: 'binary split, subnet table',
    inputs: [
      { key: 'address', label: 'Address', type: 'text', value: '192.168.10.130' },
      { key: 'prefix', label: 'Prefix /', type: 'number', value: 24, min: 0, max: 32 },
      { key: 'borrow', label: 'Borrow bits', hint: '(to make subnets)',
        type: 'number', value: 2, min: 0, max: 16 },
    ],
    build: simulate,
    draw: draw,
  });
})();
