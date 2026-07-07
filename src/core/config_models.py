from dataclasses import dataclass


@dataclass
class ApplicationConfig:
    name: str


@dataclass
class LoggingConfig:
    level: str


@dataclass
class ProviderConfig:
    type: str


@dataclass
class XOConfig:
    url: str
    username: str
    password: str
    verify_ssl: bool = True


@dataclass
class ReportConfig:
    console: bool = True


@dataclass
class Config:
    application: ApplicationConfig
    logging: LoggingConfig
    provider: ProviderConfig
    xo: XOConfig
    report: ReportConfig
