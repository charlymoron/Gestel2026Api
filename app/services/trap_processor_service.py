# ======================================================================================
# SERVICIO DE PROCESAMIENTO
# ======================================================================================
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import logger
from app.models.identificadorObjeto import IdentificadorObjeto
from app.schemas.evento_schema import EventoCreate


class TrapProcessorService:
    """Servicio para procesar archivos de traps"""

    UP_PATTERNS = [
        "LOADING to FULL",
        "is up:",
        "changed state to up",
        "state has changed from BAD to GOOD"
    ]

    DOWN_PATTERNS = [
        "FULL to DOWN",
        "is down:",
        "changed state to down",
        "state has changed from BAD to DEAD"
    ]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.ip_list: List[str] = []
        self.identificadores_cache: Dict[str, int] = {}

    async def _load_ip_list(self):
        """Cargar lista de IPs desde la base de datos"""
        try:
            query = select(IdentificadorObjeto.ValorIdentificador).where(
                IdentificadorObjeto.TipoIdentificadorId == settings.TIPO_IDENTIFICADOR_IP
            )
            result = await self.session.execute(query)
            self.ip_list = [row[0] for row in result.fetchall()]
            logger.info(f"📋 Cargadas {len(self.ip_list)} direcciones IP")
        except Exception as e:
            logger.error(f"Error cargando IPs: {str(e)}")
            raise

    async def _get_objeto_id_by_identifier(self, identifier: str) -> Optional[int]:
        """Buscar objeto por identificador con caché"""
        if not identifier:
            return None

        if identifier in self.identificadores_cache:
            return self.identificadores_cache[identifier]

        try:
            query = select(IdentificadorObjeto.ObjetoId).where(
                IdentificadorObjeto.ValorIdentificador.contains(identifier)
            ).limit(1)

            result = await self.session.execute(query)
            row = result.first()

            if row:
                objeto_id = row[0]
                self.identificadores_cache[identifier] = objeto_id
                return objeto_id

            return None
        except Exception as e:
            logger.error(f"Error buscando objeto '{identifier}': {str(e)}")
            return None

    async def _find_by_ip(self, line: str) -> Optional[int]:
        """Buscar objeto por IP en la línea"""
        for ip in self.ip_list:
            if ip in line:
                objeto_id = await self._get_objeto_id_by_identifier(ip.strip())
                if objeto_id:
                    return objeto_id
        return None

    @staticmethod
    def _extract_date(date_part: str) -> Optional[datetime]:
        """Extraer fecha de la línea"""
        try:
            parts = date_part.split('-')
            year = int(parts[0])
            month = int(parts[1])
            day_time = parts[2]

            day = int(day_time[:2])
            time_part = day_time[2:]

            time_parts = time_part.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2][:2])

            return datetime(year, month, day, hour, minute, second)
        except Exception as e:
            logger.error(f"Error parseando fecha '{date_part}': {str(e)}")
            return None

    def _determine_event_type(self, line: str) -> int:
        """Determinar tipo de evento"""
        for pattern in self.UP_PATTERNS:
            if pattern in line:
                return settings.EVENTO_UP

        for pattern in self.DOWN_PATTERNS:
            if pattern in line:
                return settings.EVENTO_DOWN

        return 0

    def _extract_useful_lines(self, file_path: Path) -> List[str]:
        """Extraer líneas útiles del archivo"""
        useful_lines = []
        all_patterns = self.UP_PATTERNS + self.DOWN_PATTERNS

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if any(pattern in line for pattern in all_patterns):
                        useful_lines.append(line.strip())

            logger.info(f"📄 Extraídas {len(useful_lines)} líneas de {file_path.name}")
            return useful_lines
        except Exception as e:
            logger.error(f"Error leyendo archivo {file_path}: {str(e)}")
            return []

    async def _process_tunnel_line(self, line: str, parts: List[str]) -> Optional[EventoCreate]:
        """Procesar línea con Tunnel"""
        try:
            if "FULL to DOWN" in line or "LOADING to FULL" in line:
                idx_tunnel = line.index("Tunnel")
                idx_from = line.index("from")
                marca = line[idx_tunnel:idx_from].strip()
            elif "changed state to down" in line or "changed state to up" in line:
                idx_tunnel = line.index("Tunnel")
                idx_changed = line.index("changed") - 2
                marca = line[idx_tunnel:idx_changed].strip()
            else:
                return None

            objeto_id = await self._get_objeto_id_by_identifier(marca)

            if not objeto_id:
                objeto_id = await self._find_by_ip(line)

            if not objeto_id:
                return None

            fecha = self._extract_date(parts[0])
            if not fecha:
                return None

            tipo_evento = self._determine_event_type(line)
            if tipo_evento == 0:
                return None

            return EventoCreate(
                ObjetoId=objeto_id,
                TipoEvento=tipo_evento,
                OperadorRegistroId=settings.DEFAULT_OPERATOR_ID,
                Fecha=fecha,
                Observaciones=[]
            )
        except Exception as e:
            logger.debug(f"Error procesando línea tunnel: {str(e)}")
            return None

    async def _process_object_name_line(self, line: str, parts: List[str]) -> Optional[EventoCreate]:
        """Procesar línea con Object_Name"""
        try:
            idx = line.index("Object_Name=")
            part_data = line[idx + 12:]
            marca = part_data.split('.')[0]

            objeto_id = await self._get_objeto_id_by_identifier(marca)

            if not objeto_id:
                return None

            fecha = self._extract_date(parts[0])
            if not fecha:
                return None

            tipo_evento = self._determine_event_type(line)
            if tipo_evento == 0:
                return None

            return EventoCreate(
                ObjetoId=objeto_id,
                TipoEvento=tipo_evento,
                OperadorRegistroId=settings.DEFAULT_OPERATOR_ID,
                Fecha=fecha,
                Observaciones=[]
            )
        except Exception as e:
            logger.debug(f"Error procesando línea object_name: {str(e)}")
            return None

    async def _process_line(self, line: str) -> Optional[EventoCreate]:
        """Procesar una línea individual"""
        parts = line.split('\t')
        if len(parts) < 2:
            return None

        if "Tunnel" in line:
            return await self._process_tunnel_line(line, parts)

        if "Object_Name=" in line:
            return await self._process_object_name_line(line, parts)

        return None

    async def process_file(self, file_path: Path) -> Dict:
        """Procesar un archivo de traps"""
        start_time = time.time()
        events: List[EventoCreate] = []
        errors: List[str] = []

        logger.info(f"🔍 Procesando archivo: {file_path.name}")

        useful_lines = self._extract_useful_lines(file_path)

        for line in useful_lines:
            try:
                event = await self._process_line(line)
                if event:
                    events.append(event)
                else:
                    errors.append(f"No se pudo procesar: {line}")
            except Exception as e:
                errors.append(f"Error: {line} - {str(e)}")

        unique_events = self._remove_duplicates(events)

        sql_file = await self._generate_sql_script(unique_events, file_path.name)
        error_file = await self._generate_error_file(errors, file_path.name) if errors else None

        processing_time = time.time() - start_time

        logger.info(
            f"✅ {file_path.name}: {len(unique_events)} eventos, "
            f"{len(errors)} errores en {processing_time:.2f}s"
        )

        return {
            "filename": file_path.name,
            "events": unique_events,
            "events_count": len(unique_events),
            "errors_count": len(errors),
            "sql_file": sql_file,
            "error_file": error_file,
            "processing_time": processing_time
        }

    @staticmethod
    def _remove_duplicates(events: List[EventoCreate]) -> List[EventoCreate]:
        """Eliminar eventos duplicados"""
        seen: Set[tuple] = set()
        unique = []

        for event in events:
            key = (event.objeto_id, event.tipo_evento, event.fecha)
            if key not in seen:
                seen.add(key)
                unique.append(event)

        return unique

    @staticmethod
    async def _generate_sql_script(events: List[EventoCreate], filename: str) -> str:
        """Generar script SQL"""
        output_path = Path(settings.OUTPUT_FOLDER)
        output_path.mkdir(exist_ok=True)

        sql_filename = f"InsertSQLEventos-{filename}.sql"
        sql_path = output_path / sql_filename

        with open(sql_path, 'w', encoding='utf-8') as f:
            f.write("BEGIN TRANSACTION;\n\n")

            for event in events:
                fecha_str = event.fecha.strftime("%Y-%m-%d %H:%M:%S")
                sql = (
                    f"INSERT INTO Evento (ObjetoId, TipoEvento, OperadorRegistroId, Fecha) "
                    f"VALUES ({event.objeto_id}, {event.tipo_evento}, "
                    f"{event.operador_registro_id}, '{fecha_str}');\n"
                )
                f.write(sql)

            f.write("\nCOMMIT;\n")
            f.write("-- ROLLBACK;\n")

        logger.info(f"📝 Script SQL: {sql_filename}")
        return str(sql_path)

    @staticmethod
    async def _generate_error_file(errors: List[str], filename: str) -> str:
        """Generar archivo de errores"""
        output_path = Path(settings.OUTPUT_FOLDER)
        output_path.mkdir(exist_ok=True)

        error_filename = f"ErroresImportant-{filename}"
        error_path = output_path / error_filename

        with open(error_path, 'w', encoding='utf-8') as f:
            for error in errors:
                f.write(f"{error}\n")

        logger.info(f"⚠️  Errores: {error_filename}")
        return str(error_path)

    async def process_all_traps(self) -> Dict:
        """Procesar todos los archivos de traps"""
        start_time = time.time()

        await self._load_ip_list()

        traps_folder = Path(settings.TRAPS_FOLDER)
        trap_files = list(traps_folder.glob("*.txt"))

        if not trap_files:
            return {
                "success": False,
                "message": "No se encontraron archivos para importar",
                "files_processed": 0,
                "total_events": 0,
                "total_errors": 0,
                "sql_files": [],
                "error_files": [],
                "processing_time": 0
            }

        logger.info(f"📦 Encontrados {len(trap_files)} archivos")

        results = []
        for file_path in trap_files:
            result = await self.process_file(file_path)
            results.append(result)

        total_events = sum(r["events_count"] for r in results)
        total_errors = sum(r["errors_count"] for r in results)
        sql_files = [r["sql_file"] for r in results if r["sql_file"]]
        error_files = [r["error_file"] for r in results if r["error_file"]]

        processing_time = time.time() - start_time

        return {
            "success": True,
            "message": "Procesamiento completado exitosamente",
            "files_processed": len(trap_files),
            "total_events": total_events,
            "total_errors": total_errors,
            "sql_files": sql_files,
            "error_files": error_files,
            "processing_time": processing_time
        }
