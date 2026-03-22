from crm import guardar_lead, obtener_estado


def agente_ventas(msg, telefono):
    msg = msg.lower()
    estado = obtener_estado(telefono)

    # 🟢 INICIO
    if estado == "inicio":
        guardar_lead(telefono, "diagnostico", mensaje=msg)
        return ("Si su clínica utiliza rayos X, existe una obligación de cumplir con protección radiológica. "
                "¿Actualmente tienen esto formalizado?")

    # 🟡 DIAGNÓSTICO
    if estado == "diagnostico":
        if "no" in msg or "no sé" in msg:
            guardar_lead(telefono, "equipo", mensaje=msg)
            return ("Entonces hay un punto crítico. Esto no es opcional. "
                    "¿Qué tipo de equipo manejan? (rayos X médico, dental, otro)")
        
        if "sí" in msg or "si" in msg:
            guardar_lead(telefono, "validacion", mensaje=msg)
            return ("Perfecto. Solo para confirmar: ¿tienen Oficial de Protección Radiológica "
                    "formalmente designado y documentado?")
    
    # 🔴 VALIDACIÓN (falso cumplimiento)
    if estado == "validacion":
        guardar_lead(telefono, "riesgo", mensaje=msg)
        return ("Ahí es donde normalmente aparecen los problemas. No basta con tener a alguien, "
                "debe estar formalizado.")
    
    # 🔵 EQUIPO
    if estado == "equipo":
        guardar_lead(telefono, "riesgo", mensaje=msg)
        return ("Le explico algo claro: muchas clínicas creen que están cumpliendo, pero en inspección "
                "es donde aparecen los problemas.")
    
    # 🟣 RIESGO → SOLUCIÓN
    if estado == "riesgo":
        guardar_lead(telefono, "cierre", mensaje=msg)
        return ("Nos encargamos de que su clínica cumpla con la obligación legal de protección radiológica "
                "y tenga respaldo técnico y legal ante cualquier inspección o incidente.\n\n"
                "Si quiere, le hago una evaluación rápida sin costo.\n"
                "¿En qué ciudad se encuentra?")
    
    # ⚫ CIERRE
    if estado == "cierre":
        guardar_lead(telefono, "final", ciudad=msg, mensaje=msg)
        return ("Perfecto. Con eso podemos orientarle mejor.\n"
                "Le contacto para coordinar la evaluación inicial.")

    return "Cuénteme un poco más sobre su clínica."