"""UI localization helpers for BL-23 (English/Spanish interface text)."""

from __future__ import annotations

from typing import TypedDict


SupportedLanguage = str
DEFAULT_LANGUAGE: SupportedLanguage = "en"
SUPPORTED_LANGUAGES: set[SupportedLanguage] = {"en", "es"}


class UIStrs(TypedDict):
    notes_count_label: str
    create_note: str
    search_notes: str
    search_placeholder: str
    clear: str
    view_trash: str
    lock_tooltip: str
    change_private_pin: str
    notes_title: str
    notes_title_trash: str
    newest_first: str
    selected_suffix: str
    selected_notes_summary: str
    select_all: str
    unselect_all: str
    delete_forever: str
    delete_selected: str
    restore: str
    idle_title: str
    idle_copy: str
    cancel: str
    delete: str
    move_note_to_trash: str
    move_selected_to_trash: str
    delete_forever_heading: str
    restore_window_copy: str
    permanent_delete_copy: str
    search_empty_no_notes: str
    search_empty_no_match: str
    trash_empty_no_match: str
    trash_empty: str
    trash_group_title: str
    today_group: str
    previous_seven_days_group: str
    private_note: str
    note_empty: str
    deleted_recently: str
    deleted_prefix: str
    note_not_found: str
    pin_data_decrypt_warning: str
    pin_data_hidden_warning: str
    unlock_title: str
    unlock_subtitle: str
    unlock_wrong_pin: str
    unlock_correct_pin: str
    edit_note: str
    save_edits: str
    delete_note: str
    edit_subtitle: str
    title_label: str
    body_label: str
    created_label: str
    modified_label: str
    deleted_label: str
    private_note_toggle: str
    bullets: str
    checklist: str
    trash_note_title: str
    trash_note_subtitle: str
    create_panel_title: str
    create_panel_subtitle: str
    title_placeholder: str
    body_placeholder: str
    create_note_submit: str
    create_note_microcopy: str
    pin_settings_title: str
    pin_settings_subtitle: str
    pin_settings_recovery_copy: str
    show_pin_digits: str
    current_pin_label: str
    verify_current_pin: str
    current_pin_verified: str
    new_pin_label: str
    confirm_new_pin_label: str
    save_pin: str


_UI_STRINGS: dict[SupportedLanguage, UIStrs] = {
    "en": {
        "notes_count_label": "Notes",
        "create_note": "Create Note",
        "search_notes": "Search notes",
        "search_placeholder": "Search title or content",
        "clear": "Clear",
        "view_trash": "View Trash",
        "lock_tooltip": "Default pin is 1234 until changed",
        "change_private_pin": "Change Private Pin",
        "notes_title": "Notes",
        "notes_title_trash": "Notes in Trash",
        "newest_first": "Newest first",
        "selected_suffix": "selected",
        "selected_notes_summary": "{count} selected notes",
        "select_all": "Select all",
        "unselect_all": "Unselect all",
        "delete_forever": "Delete Forever",
        "delete_selected": "Delete selected",
        "restore": "Restore",
        "idle_title": "Ready when you are",
        "idle_copy": "Select a note to edit, or click Create Note.",
        "cancel": "Cancel",
        "delete": "Delete",
        "move_note_to_trash": "Move note to trash?",
        "move_selected_to_trash": "Move {count} notes to trash?",
        "delete_forever_heading": "Delete forever?",
        "restore_window_copy": "You can restore this note from Trash for 15 days.",
        "permanent_delete_copy": "This permanently deletes the note and cannot be undone.",
        "search_empty_no_notes": "No notes yet. Create your first note.",
        "search_empty_no_match": "No notes match your search.",
        "trash_empty_no_match": "No deleted notes match your search.",
        "trash_empty": "Trash is empty.",
        "trash_group_title": "Trash (auto-purged after 15 days)",
        "today_group": "Today",
        "previous_seven_days_group": "Previous 7 days",
        "private_note": "Private note",
        "note_empty": "Note is empty",
        "deleted_recently": "recently",
        "deleted_prefix": "Deleted",
        "note_not_found": "Note not found",
        "pin_data_decrypt_warning": "Private note data could not be decrypted with current PIN settings. Open Private PIN and restore the last valid PIN before changing it again.",
        "pin_data_hidden_warning": "Notes are temporarily hidden until PIN settings are corrected.",
        "unlock_title": "Unlock",
        "unlock_subtitle": "This note is private. Enter your 4-digit PIN to continue.",
        "unlock_wrong_pin": "Enter correct pin to unlock private note.",
        "unlock_correct_pin": "Enter correct pin to unlock private note.",
        "edit_note": "Edit Note",
        "save_edits": "Save edits",
        "delete_note": "Delete",
        "edit_subtitle": "Edit the selected note. Save applies your changes and keeps this panel open.",
        "title_label": "Title",
        "body_label": "Body",
        "created_label": "Created",
        "modified_label": "Modified",
        "deleted_label": "Deleted",
        "private_note_toggle": "Private note",
        "bullets": "Bullets",
        "checklist": "Checklist",
        "trash_note_title": "Trash Note",
        "trash_note_subtitle": "This note is in Trash and is read-only. Restore it to make edits.",
        "create_panel_title": "New Note",
        "create_panel_subtitle": "Create a new note here. Closing this panel returns you to the notes list only.",
        "title_placeholder": "Example: Sprint check-in summary",
        "body_placeholder": "Add details, context, and next steps...",
        "create_note_submit": "Create Note",
        "create_note_microcopy": "Validation is enforced server-side through NoteService, then rendered back as inline feedback.",
        "pin_settings_title": "Private PIN Settings",
        "pin_settings_subtitle": "Default PIN is 1234. Set a new 4-digit numeric PIN for private notes.",
        "pin_settings_recovery_copy": "If notes were encrypted under a previous PIN after a manual config edit, enter that previous PIN as Current PIN to recover.",
        "show_pin_digits": "Show PIN digits",
        "current_pin_label": "Current PIN",
        "verify_current_pin": "Verify Current PIN",
        "current_pin_verified": "Current PIN (verified)",
        "new_pin_label": "New PIN",
        "confirm_new_pin_label": "Confirm new PIN",
        "save_pin": "Save PIN",
    },
    "es": {
        "notes_count_label": "Notas",
        "create_note": "Crear nota",
        "search_notes": "Buscar notas",
        "search_placeholder": "Buscar por titulo o contenido",
        "clear": "Limpiar",
        "view_trash": "Ver papelera",
        "lock_tooltip": "El PIN por defecto es 1234 hasta cambiarlo",
        "change_private_pin": "Cambiar PIN privado",
        "notes_title": "Notas",
        "notes_title_trash": "Notas en papelera",
        "newest_first": "Mas recientes primero",
        "selected_suffix": "seleccionadas",
        "selected_notes_summary": "{count} notas seleccionadas",
        "select_all": "Seleccionar todo",
        "unselect_all": "Deseleccionar todo",
        "delete_forever": "Eliminar para siempre",
        "delete_selected": "Eliminar seleccionadas",
        "restore": "Restaurar",
        "idle_title": "Listo cuando quieras",
        "idle_copy": "Selecciona una nota para editar o haz clic en Crear nota.",
        "cancel": "Cancelar",
        "delete": "Eliminar",
        "move_note_to_trash": "Mover nota a la papelera?",
        "move_selected_to_trash": "Mover {count} notas a la papelera?",
        "delete_forever_heading": "Eliminar para siempre?",
        "restore_window_copy": "Puedes restaurar esta nota desde la papelera durante 15 dias.",
        "permanent_delete_copy": "Esto elimina la nota de forma permanente y no se puede deshacer.",
        "search_empty_no_notes": "Aun no hay notas. Crea tu primera nota.",
        "search_empty_no_match": "No hay notas que coincidan con tu busqueda.",
        "trash_empty_no_match": "No hay notas eliminadas que coincidan con tu busqueda.",
        "trash_empty": "La papelera esta vacia.",
        "trash_group_title": "Papelera (se elimina automaticamente despues de 15 dias)",
        "today_group": "Hoy",
        "previous_seven_days_group": "Ultimos 7 dias",
        "private_note": "Nota privada",
        "note_empty": "La nota esta vacia",
        "deleted_recently": "recientemente",
        "deleted_prefix": "Eliminada",
        "note_not_found": "Nota no encontrada",
        "pin_data_decrypt_warning": "No se pudo descifrar la informacion de notas privadas con la configuracion actual del PIN. Abre PIN privado y restaura el ultimo PIN valido antes de cambiarlo otra vez.",
        "pin_data_hidden_warning": "Las notas estan ocultas temporalmente hasta corregir la configuracion del PIN.",
        "unlock_title": "Desbloquear",
        "unlock_subtitle": "Esta nota es privada. Ingresa tu PIN de 4 digitos para continuar.",
        "unlock_wrong_pin": "Ingresa el PIN correcto para desbloquear la nota privada.",
        "unlock_correct_pin": "Ingresa el PIN correcto para desbloquear la nota privada.",
        "edit_note": "Editar nota",
        "save_edits": "Guardar cambios",
        "delete_note": "Eliminar",
        "edit_subtitle": "Edita la nota seleccionada. Guardar aplica los cambios y mantiene este panel abierto.",
        "title_label": "Titulo",
        "body_label": "Contenido",
        "created_label": "Creada",
        "modified_label": "Modificada",
        "deleted_label": "Eliminada",
        "private_note_toggle": "Nota privada",
        "bullets": "Vinetas",
        "checklist": "Checklist",
        "trash_note_title": "Nota en papelera",
        "trash_note_subtitle": "Esta nota esta en la papelera y es solo lectura. Restaurala para editar.",
        "create_panel_title": "Nueva nota",
        "create_panel_subtitle": "Crea una nueva nota aqui. Al cerrar este panel vuelves a la lista de notas.",
        "title_placeholder": "Ejemplo: Resumen de sprint",
        "body_placeholder": "Agrega detalles, contexto y siguientes pasos...",
        "create_note_submit": "Crear nota",
        "create_note_microcopy": "La validacion se aplica en el servidor con NoteService y se muestra como retroalimentacion en linea.",
        "pin_settings_title": "Configuracion de PIN privado",
        "pin_settings_subtitle": "El PIN por defecto es 1234. Define un nuevo PIN numerico de 4 digitos para notas privadas.",
        "pin_settings_recovery_copy": "Si las notas fueron cifradas con un PIN previo tras una edicion manual de config, ingresa ese PIN previo como PIN actual para recuperar.",
        "show_pin_digits": "Mostrar digitos del PIN",
        "current_pin_label": "PIN actual",
        "verify_current_pin": "Verificar PIN actual",
        "current_pin_verified": "PIN actual (verificado)",
        "new_pin_label": "Nuevo PIN",
        "confirm_new_pin_label": "Confirmar nuevo PIN",
        "save_pin": "Guardar PIN",
    },
}


def resolve_ui_language(query_lang: str | None, cookie_lang: str | None) -> SupportedLanguage:
    candidate = (query_lang or cookie_lang or DEFAULT_LANGUAGE).strip().lower()
    if candidate in SUPPORTED_LANGUAGES:
        return candidate
    return DEFAULT_LANGUAGE


def get_ui_strings(lang: SupportedLanguage) -> UIStrs:
    return _UI_STRINGS.get(lang, _UI_STRINGS[DEFAULT_LANGUAGE])
