library(sf)
library(tidyverse)
raw_file <- rio::import('data/domain_winner.csv') %>%
  select(!dominance) %>%
  rename(COUNTYNAME = City, TOWNNAME = Town) %>%
  bind_rows(data.frame(
    COUNTYNAME = c("臺東縣", "屏東縣", "臺南市", "金門縣", "臺東縣"),
    TOWNNAME = c("延平鄉", "牡丹鄉", "左鎮區", "烏坵鄉", "金峰鄉")
  )) %>%
  mutate(across(`7-11`:familymart, replace_na, 0))
cs_file <- raw_file %>%
  pivot_longer(cols = `7-11`:familymart) %>%
  group_by(COUNTYNAME, TOWNNAME) %>%
  arrange(desc(value), .by_group = TRUE, decreasing = TRUE)

first <- slice(cs_file, 1) %>%
  rename(first_name = name, first_value = value)
second <- slice(cs_file, 2) %>% slice_tail() %>%
  rename(second_name = name, second_value = value)
third <- slice(cs_file, 3) %>% slice_tail() %>%
  rename(third_name = name, third_value = value)
fourth <- slice(cs_file, 4) %>% slice_tail() %>%
  rename(fourth_name = name, fourth_value = value)
complete_rank <-
  first %>% full_join(second) %>% full_join(third) %>% full_join(fourth) %>%
  mutate(
    First_place =
      case_when(
        first_value + second_value + third_value + fourth_value == 0 ~ "Forgotten Place",
        first_value - second_value == 0 ~ sprintf("Draw [%s, %s]", first_name, second_name),
        TRUE ~ first_name
      ),
    leading_num = first_value - second_value,
    competing = leading_num == 1 & second_value != 0,
    second_color = if_else(competing, second_name, ""),
    First_place = factor(
      First_place,
      levels = c(
        "7-11",
        "Draw [7-11, familymart]",
        "Draw [7-11, okmart]",
        "familymart",
        "Forgotten Place"
      ),
      labels = c(
        "7-11",
        "Draw [7-11, FamilyMart]",
        "Draw [7-11, OK]",
        "FamilyMart",
        "Forgotten Place"
      )
    ),
    first_percent = if_else((first_value + second_value + third_value + fourth_value) != 0,
                            first_value / (first_value + second_value + third_value + fourth_value),
                            0
    )
  )

color_711 <- "#438939"
color_7_f <- "#56b04a"
color_7_o <- "#8a8439"
color_familymart <- "#4485c9"
color_okmart <- "#d8360c"
color_hilife <- "#b6331b"

taiwan_map <- sf::read_sf("data/taiwan/TOWN_MOI_1111118.shp") %>%
  full_join(complete_rank, by = c("COUNTYNAME", "TOWNNAME"))
tm_711 <- taiwan_map[taiwan_map$First_place == "7-11", ]
tm_7f <-
  taiwan_map[taiwan_map$First_place == "Draw [7-11, FamilyMart]", ]
tm_7o <- taiwan_map[taiwan_map$First_place == "Draw [7-11, OK]", ]
tm_fm <- taiwan_map[taiwan_map$First_place == "FamilyMart", ]
tm_fp <- taiwan_map[taiwan_map$First_place == "Forgotten Place", ]


(
  tw_map <- ggplot() +
    geom_sf(data = tm_711, aes(fill = first_percent)) +
    scale_fill_gradient(
      name = "7-11",
      low = "white",
      high = color_711,
      breaks = 0.25*0:4, labels = scales::percent(0.25*0:4)
    ) +
    ggnewscale::new_scale_fill() +
    geom_sf(data = tm_fm, aes(fill = first_percent)) +
    scale_fill_gradient(
      name = "FamilyMart",
      low = "white",
      high = color_familymart,
      breaks = 0.25*0:4, labels = scales::percent(0.25*0:4)
    ) +
    ggnewscale::new_scale_fill() +
    geom_sf(data = tm_7f, aes(fill = First_place)) +
    geom_sf(data = tm_7o, aes(fill = First_place)) +
    geom_sf(data = tm_fp, aes(fill = First_place)) +
    coord_sf(
      xlim = c(118, 124),
      ylim = c(21.5, 26.5),
      expand = FALSE
    ) +
    theme_bw() +
    theme(
      panel.background = element_rect(fill = "lightblue"),
      legend.position = "top"
    ) +
    scale_fill_manual(
      name = "",
      values = c(
        `Forgotten Place` = "GREY",
        `Draw [7-11, FamilyMart]` = color_7_f,
        `Draw [7-11, OK]` = color_7_o
      )
    )
)
ggsave("percent_v.png")
