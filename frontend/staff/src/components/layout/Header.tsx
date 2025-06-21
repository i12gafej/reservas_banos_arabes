import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FiMenu, FiX, FiUser, FiPower } from 'react-icons/fi';

import './header.css';

const menuItems = [
  { label: 'Cuadrante', path: '/cuadrante' },
  { label: 'Masajistas', path: '/masajistas' },
  { label: 'Reservar', path: '/reservar' },
  { label: 'Cheques', path: '/cheques' },
  { label: 'Clientes', path: '/clientes' },
  { label: 'Facturación', path: '/facturacion' },
  { label: 'Productos', path: '/productos' },
  { label: 'Gestión general', path: '/gestion' },
];

const Header: React.FC = () => {
  const [open, setOpen] = useState(false);
  const userName = 'Admin'; // TODO: traer del contexto de auth

  return (
    <header className="topbar">
      {/* Logo / título */}
      <div className="brand">Baños Árabes</div>

      {/* Botón móvil */}
      <button className="burger" onClick={() => setOpen(!open)}>
        {open ? <FiX /> : <FiMenu />}
      </button>

      {/* Navegación */}
      <nav className={`nav ${open ? 'open' : ''}`} onClick={() => setOpen(false)}>
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => (isActive ? 'link active' : 'link')}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Usuario */}
      <div className="user-area">
        <FiUser className="user-icon" />
        <span className="user-name">{userName}</span>
        <button className="logout">
          <FiPower />
        </button>
      </div>
    </header>
  );
};

export default Header; 