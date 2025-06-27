#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para insertar 30 reservas de prueba con masajes variados
Fecha: 29/06/2025
Ejecutar desde: docker exec -it aplicacion-backend-1 python test_massage_data.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date
import random

# Configurar Django
sys.path.append('/app/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings.dev')
django.setup()

from reservations.models import Client, Product, BathType, ProductBaths, Book
from reservations.managers.book import BookManager

def create_test_data():
    """Crear 30 reservas de prueba con masajes variados para el 29/06/2025"""
    
    # Asegurar que existen todos los tipos de baño
    BookManager.ensure_bath_types_exist()
    
    # Datos ficticios de clientes
    clientes_data = [
        ("María", "García López", "34666123456", "maria.garcia@email.com"),
        ("Carlos", "Rodríguez Pérez", "34677234567", "carlos.rodriguez@email.com"),
        ("Ana", "Martínez Silva", "34688345678", "ana.martinez@email.com"),
        ("Luis", "Fernández Ruiz", "34699456789", "luis.fernandez@email.com"),
        ("Carmen", "López García", "34600567890", "carmen.lopez@email.com"),
        ("Miguel", "Sánchez Torres", "34611678901", "miguel.sanchez@email.com"),
        ("Elena", "Jiménez Moreno", "34622789012", "elena.jimenez@email.com"),
        ("David", "Morales Herrera", "34633890123", "david.morales@email.com"),
        ("Lucía", "Herrera Castro", "34644901234", "lucia.herrera@email.com"),
        ("Javier", "Castro Ortega", "34655012345", "javier.castro@email.com"),
        ("Pilar", "Ortega Delgado", "34666123457", "pilar.ortega@email.com"),
        ("Roberto", "Delgado Vega", "34677234568", "roberto.delgado@email.com"),
        ("Sandra", "Vega Romero", "34688345679", "sandra.vega@email.com"),
        ("Fernando", "Romero Gil", "34699456780", "fernando.romero@email.com"),
        ("Isabel", "Gil Medina", "34600567891", "isabel.gil@email.com"),
        ("Alberto", "Medina Ramos", "34611678902", "alberto.medina@email.com"),
        ("Beatriz", "Ramos Guerrero", "34622789013", "beatriz.ramos@email.com"),
        ("Sergio", "Guerrero Cortés", "34633890124", "sergio.guerrero@email.com"),
        ("Cristina", "Cortés Vargas", "34644901235", "cristina.cortes@email.com"),
        ("Raúl", "Vargas Campos", "34655012346", "raul.vargas@email.com"),
        ("Patricia", "Campos Rubio", "34666123458", "patricia.campos@email.com"),
        ("Andrés", "Rubio Pascual", "34677234569", "andres.rubio@email.com"),
        ("Mónica", "Pascual Marín", "34688345680", "monica.pascual@email.com"),
        ("Francisco", "Marín Iglesias", "34699456781", "francisco.marin@email.com"),
        ("Silvia", "Iglesias Peña", "34600567892", "silvia.iglesias@email.com"),
        ("Pablo", "Peña Aguilar", "34611678903", "pablo.pena@email.com"),
        ("Gloria", "Aguilar Santos", "34622789014", "gloria.aguilar@email.com"),
        ("Jorge", "Santos León", "34633890125", "jorge.santos@email.com"),
        ("Alicia", "León Mendoza", "34644901236", "alicia.leon@email.com"),
        ("Iván", "Mendoza Flores", "34655012347", "ivan.mendoza@email.com"),
    ]
    
    # Configuraciones de masajes variadas
    configuraciones_masajes = [
        # Solo masajes de 60 minutos
        {"massage60Relax": 1, "people": 1},
        {"massage60Relax": 2, "people": 2},
        {"massage60Piedra": 1, "people": 1},
        {"massage60Exfol": 1, "people": 1},
        {"massage60Relax": 1, "massage60Piedra": 1, "people": 2},
        
        # Solo masajes de 30 minutos
        {"massage30Relax": 1, "people": 1},
        {"massage30Relax": 2, "people": 2},
        {"massage30Piedra": 1, "people": 1},
        {"massage30Exfol": 1, "people": 1},
        {"massage30Relax": 1, "massage30Exfol": 1, "people": 2},
        
        # Solo masajes de 15 minutos
        {"massage15Relax": 1, "people": 1},
        {"massage15Relax": 2, "people": 2},
        {"massage15Relax": 3, "people": 3},
        
        # Combinaciones mixtas
        {"massage60Relax": 1, "massage30Relax": 1, "people": 2},
        {"massage60Piedra": 1, "massage15Relax": 1, "people": 2},
        {"massage30Relax": 1, "massage30Piedra": 1, "people": 2},
        {"massage60Exfol": 1, "massage30Exfol": 1, "people": 2},
        {"massage15Relax": 2, "massage30Relax": 1, "people": 3},
        
        # Configuraciones para grupos grandes
        {"massage60Relax": 2, "massage30Relax": 1, "people": 4},
        {"massage60Piedra": 1, "massage60Exfol": 1, "massage15Relax": 1, "people": 4},
        {"massage30Relax": 3, "people": 5},
        {"massage60Relax": 1, "massage30Relax": 2, "massage15Relax": 1, "people": 5},
        
        # Configuraciones más complejas
        {"massage60Relax": 2, "massage60Piedra": 1, "people": 4},
        {"massage30Relax": 2, "massage30Exfol": 1, "massage15Relax": 1, "people": 5},
        {"massage60Exfol": 1, "massage30Relax": 1, "massage30Piedra": 1, "people": 4},
        {"massage15Relax": 4, "people": 6},
        {"massage60Relax": 1, "massage60Piedra": 1, "massage60Exfol": 1, "people": 4},
        {"massage30Relax": 1, "massage30Piedra": 1, "massage30Exfol": 1, "massage15Relax": 1, "people": 5},
        
        # Últimas configuraciones variadas
        {"massage60Relax": 3, "people": 4},
        {"massage30Piedra": 2, "massage15Relax": 2, "people": 5},
    ]
    
    # Comentarios variados
    comentarios = [
        "Cliente VIP - Trato especial",
        "Primera visita - Explicar servicios",
        "Aniversario de bodas",
        "Regalo de cumpleaños",
        "Cliente con problemas de espalda",
        "Viene en grupo familiar",
        "Celebración especial",
        "Cliente habitual",
        "Masaje relajante después del trabajo",
        "Sesión de desestresamiento",
        "Tratamiento terapéutico",
        "Masaje deportivo",
        "Sesión de pareja",
        "Despedida de soltera",
        "Evento corporativo",
        "",  # Sin comentario
        "Cliente con alergia - usar aceites hipoalergénicos",
        "Prefiere masajista femenina",
        "Masaje suave - cliente sensible",
        "Sesión intensiva",
    ]
    
    # Horas de reserva (10:00 a 21:30 cada 30 minutos)
    horas_reserva = [
        "10:00:00", "10:30:00", "11:00:00", "11:30:00", "12:00:00", "12:30:00",
        "13:00:00", "13:30:00", "14:00:00", "14:30:00", "15:00:00", "15:30:00",
        "16:00:00", "16:30:00", "17:00:00", "17:30:00", "18:00:00", "18:30:00",
        "19:00:00", "19:30:00", "20:00:00", "20:30:00", "21:00:00", "21:30:00"
    ]
    
    print("🏗️  Iniciando creación de 30 reservas de prueba con masajes...")
    print("📅 Fecha: 29/06/2025")
    print("=" * 60)
    
    reservas_creadas = 0
    
    for i in range(30):
        try:
            # Crear o obtener cliente
            client_data = clientes_data[i]
            client, created = Client.objects.get_or_create(
                phone_number=client_data[2],
                defaults={
                    'name': client_data[0],
                    'surname': client_data[1],
                    'email': client_data[3],
                }
            )
            
            if created:
                print(f"✅ Cliente creado: {client.name} {client.surname}")
            
            # Obtener configuración de masajes
            config = configuraciones_masajes[i]
            people = config.pop('people')  # Extraer people antes de procesar masajes
            
            # Convertir configuración a lista de baths
            from reservations.dtos.book import StaffBathRequestDTO
            baths = []
            
            # Mapeo de campos a tipos de masaje
            massage_map = {
                'massage60Relax': ('relax', '60'),
                'massage60Piedra': ('rock', '60'), 
                'massage60Exfol': ('exfoliation', '60'),
                'massage30Relax': ('relax', '30'),
                'massage30Piedra': ('rock', '30'),
                'massage30Exfol': ('exfoliation', '30'),
                'massage15Relax': ('relax', '15'),
            }
            
            # Contar total de masajes
            total_massages = 0
            for field_name, (massage_type, duration) in massage_map.items():
                quantity = config.get(field_name, 0)
                if quantity > 0:
                    baths.append(StaffBathRequestDTO(
                        massage_type=massage_type,
                        minutes=duration,
                        quantity=quantity
                    ))
                    total_massages += quantity
            
            # Agregar baños sin masaje para las personas restantes
            people_without_massage = people - total_massages
            if people_without_massage > 0:
                baths.append(StaffBathRequestDTO(
                    massage_type='none',
                    minutes='0',
                    quantity=people_without_massage
                ))
            
            # Si no hay masajes ni baños, agregar baños sin masaje para todas las personas
            if not baths:
                baths.append(StaffBathRequestDTO(
                    massage_type='none',
                    minutes='0',
                    quantity=people
                ))
            
            # Seleccionar hora aleatoria
            hora = random.choice(horas_reserva)
            
            # Seleccionar comentario aleatorio
            comentario = random.choice(comentarios)
            
            # Crear reserva usando el manager
            booking_dto = BookManager.create_booking_from_staff(
                baths=baths,
                name=client.name,
                surname=client.surname,
                phone=client.phone_number,
                email=client.email,
                date="2025-06-29",
                hour=hora,
                people=people,
                comment=comentario,
                force=True  # Forzar para evitar validaciones de disponibilidad
            )
            
            # Describir masajes creados
            masajes_desc = []
            for bath in baths:
                if bath.massage_type != 'none':
                    tipo_esp = {
                        'relax': 'Relajante',
                        'rock': 'Piedras',
                        'exfoliation': 'Exfoliante'
                    }.get(bath.massage_type, bath.massage_type)
                    masajes_desc.append(f"{bath.quantity}x {tipo_esp} {bath.minutes}'")
            
            masajes_str = ", ".join(masajes_desc) if masajes_desc else "Solo baños"
            
            print(f"📋 Reserva {i+1:2d}: {client.name} {client.surname[:10]:10s} | {hora} | {people}p | {masajes_str}")
            
            reservas_creadas += 1
            
        except Exception as e:
            print(f"❌ Error creando reserva {i+1}: {str(e)}")
            continue
    
    print("=" * 60)
    print(f"✅ Proceso completado!")
    print(f"📊 Reservas creadas: {reservas_creadas}/30")
    print(f"📅 Fecha: 29 de junio de 2025")
    print(f"💆 Todas las reservas incluyen diferentes tipos de masajes")
    print("\n🔍 Para ver las reservas en la interfaz:")
    print("   1. Ve a la página Cuadrante")
    print("   2. Selecciona la fecha: 29/06/2025")
    print("   3. Haz clic en 'Ver cuadrante'")
    print("   4. Verás la nueva tabla 'Masajes del día' con todas las reservas")

if __name__ == "__main__":
    create_test_data() 