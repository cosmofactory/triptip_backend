"""20240801122150

Revision ID: fb40e8d83b0a
Revises: 8ebb55d31f46
Create Date: 2024-08-01 12:21:50.738021

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fb40e8d83b0a"
down_revision: Union[str, None] = "8ebb55d31f46"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    region_enum = sa.Enum(
        "ASIA",
        "EUROPE",
        "AFRICA",
        "NORTH_AMERICA",
        "SOUTH_AMERICA",
        "OCEANIA",
        "AFGHANISTAN",
        "ALBANIA",
        "ALGERIA",
        "AMERICAN_SAMOA",
        "ANDORRA",
        "ANGOLA",
        "ANGUILLA",
        "ANTARCTICA",
        "ANTIGUA_AND_BARBUDA",
        "ARGENTINA",
        "ARMENIA",
        "ARUBA",
        "AUSTRALIA",
        "AUSTRIA",
        "AZERBAIJAN",
        "BAHAMAS",
        "BAHRAIN",
        "BANGLADESH",
        "BARBADOS",
        "BELARUS",
        "BELGIUM",
        "BELIZE",
        "BENIN",
        "BERMUDA",
        "BHUTAN",
        "BOLIVIA",
        "BONAIRE",
        "BOSNIA_AND_HERZEGOVINA",
        "BOTSWANA",
        "BOUVET_ISLAND",
        "BRAZIL",
        "BRITISH_INDIAN_OCEAN_TERRITORY",
        "BRUNEI_DARUSSALAM",
        "BULGARIA",
        "BURKINA_FASO",
        "BURUNDI",
        "CABO_VERDE",
        "CAMBODIA",
        "CAMEROON",
        "CANADA",
        "CAYMAN_ISLANDS",
        "CENTRAL_AFRICAN_REPUBLIC",
        "CHAD",
        "CHILE",
        "CHINA",
        "CHRISTMAS_ISLAND",
        "COCOS_ISLANDS",
        "COLOMBIA",
        "COMOROS",
        "CONGO_DR",
        "CONGO",
        "COOK_ISLANDS",
        "COSTA_RICA",
        "CROATIA",
        "CUBA",
        "CURACAO",
        "CYPRUS",
        "CZECHIA",
        "COTE_DIVOIRE",
        "DENMARK",
        "DJIBOUTI",
        "DOMINICA",
        "DOMINICAN_REPUBLIC",
        "ECUADOR",
        "EGYPT",
        "EL_SALVADOR",
        "EQUATORIAL_GUINEA",
        "ERITREA",
        "ESTONIA",
        "ESWATINI",
        "ETHIOPIA",
        "FALKLAND_ISLANDS",
        "FAROE_ISLANDS",
        "FIJI",
        "FINLAND",
        "FRANCE",
        "FRENCH_GUIANA",
        "FRENCH_POLYNESIA",
        "FRENCH_SOUTHERN_TERRITORIES",
        "GABON",
        "GAMBIA",
        "GEORGIA",
        "GERMANY",
        "GHANA",
        "GIBRALTAR",
        "GREECE",
        "GREENLAND",
        "GRENADA",
        "GUADELOUPE",
        "GUAM",
        "GUATEMALA",
        "GUERNSEY",
        "GUINEA",
        "GUINEA_BISSAU",
        "GUYANA",
        "HAITI",
        "HEARD_ISLAND",
        "HOLY_SEE",
        "HONDURAS",
        "HONG_KONG",
        "HUNGARY",
        "ICELAND",
        "INDIA",
        "INDONESIA",
        "IRAN",
        "IRAQ",
        "IRELAND",
        "ISLE_OF_MAN",
        "ISRAEL",
        "ITALY",
        "JAMAICA",
        "JAPAN",
        "JERSEY",
        "JORDAN",
        "KAZAKHSTAN",
        "KENYA",
        "KIRIBATI",
        "KOREA_DR",
        "KOREA_REP",
        "KUWAIT",
        "KYRGYZSTAN",
        "LAO_PDR",
        "LATVIA",
        "LEBANON",
        "LESOTHO",
        "LIBERIA",
        "LIBYA",
        "LIECHTENSTEIN",
        "LITHUANIA",
        "LUXEMBOURG",
        "MACAO",
        "MADAGASCAR",
        "MALAWI",
        "MALAYSIA",
        "MALDIVES",
        "MALI",
        "MALTA",
        "MARSHALL_ISLANDS",
        "MARTINIQUE",
        "MAURITANIA",
        "MAURITIUS",
        "MAYOTTE",
        "MEXICO",
        "MICRONESIA",
        "MOLDOVA",
        "MONACO",
        "MONGOLIA",
        "MONTENEGRO",
        "MONTSERRAT",
        "MOROCCO",
        "MOZAMBIQUE",
        "MYANMAR",
        "NAMIBIA",
        "NAURU",
        "NEPAL",
        "NETHERLANDS",
        "NEW_CALEDONIA",
        "NEW_ZEALAND",
        "NICARAGUA",
        "NIGER",
        "NIGERIA",
        "NIUE",
        "NORFOLK_ISLAND",
        "NORTHERN_MARIANA_ISLANDS",
        "NORWAY",
        "OMAN",
        "PAKISTAN",
        "PALAU",
        "PALESTINE",
        "PANAMA",
        "PAPUA_NEW_GUINEA",
        "PARAGUAY",
        "PERU",
        "PHILIPPINES",
        "PITCAIRN",
        "POLAND",
        "PORTUGAL",
        "PUERTO_RICO",
        "QATAR",
        "NORTH_MACEDONIA",
        "ROMANIA",
        "RUSSIAN_FEDERATION",
        "RWANDA",
        "REUNION",
        "SAINT_BARTHELEMY",
        "SAINT_HELENA",
        "SAINT_KITTS_AND_NEVIS",
        "SAINT_LUCIA",
        "SAINT_MARTIN_FR",
        "SAINT_PIERRE_AND_MIQUELON",
        "SAINT_VINCENT_AND_THE_GRENADINES",
        "SAMOA",
        "SAN_MARINO",
        "SAO_TOME_AND_PRINCIPE",
        "SAUDI_ARABIA",
        "SENEGAL",
        "SERBIA",
        "SEYCHELLES",
        "SIERRA_LEONE",
        "SINGAPORE",
        "SINT_MAARTEN",
        "SLOVAKIA",
        "SLOVENIA",
        "SOLOMON_ISLANDS",
        "SOMALIA",
        "SOUTH_AFRICA",
        "SOUTH_GEORGIA",
        "SOUTH_SUDAN",
        "SPAIN",
        "SRI_LANKA",
        "SUDAN",
        "SURINAME",
        "SVALBARD_AND_JAN_MAYEN",
        "SWEDEN",
        "SWITZERLAND",
        "SYRIA",
        "TAIWAN",
        "TAJIKISTAN",
        "TANZANIA",
        "THAILAND",
        "TIMOR_LESTE",
        "TOGO",
        "TOKELAU",
        "TONGA",
        "TRINIDAD_AND_TOBAGO",
        "TUNISIA",
        "TURKEY",
        "TURKMENISTAN",
        "TURKS_AND_CAICOS",
        "TUVALU",
        "UGANDA",
        "UKRAINE",
        "UAE",
        "UK",
        "US_OUTLYING_ISLANDS",
        "USA",
        "URUGUAY",
        "UZBEKISTAN",
        "VANUATU",
        "VENEZUELA",
        "VIET_NAM",
        "VIRGIN_ISLANDS_BR",
        "VIRGIN_ISLANDS_US",
        "WALLIS_AND_FUTUNA",
        "WESTERN_SAHARA",
        "YEMEN",
        "ZAMBIA",
        "ZIMBABWE",
        "ALAND_ISLANDS",
        name="regionenum",
    )

    region_enum.create(op.get_bind(), checkfirst=True)  # Create the enum type in the database

    op.add_column(
        "trips",
        sa.Column(
            "region",
            region_enum,
            nullable=False,
            server_default="FRANCE",
        ),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("trips", "region")
    # ### end Alembic commands ###