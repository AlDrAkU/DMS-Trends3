from abc import ABC, abstractmethod

class FileStorageRepository(ABC):
    @abstractmethod
    def insert(self, filepath: str, temp_or_perm: str, status: str) -> None:
        """
        Insert a new row into the FileStorage table.

        :param filepath: File path
        :param temp_or_perm: Temporary or Permanent status
        :param status: Status (Active or Deleted)
        :return: None
        """
        pass

    # Function that fetches one row from the FileStorage table by UUID and returns it
    @abstractmethod
    def fetch_one(self, uuid: str):
        """
        Fetch one row from the FileStorage table by UUID.

        :param uuid: UUID
        :return: Query
        """
        pass