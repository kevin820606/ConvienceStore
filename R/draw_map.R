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

tw_map <- ggplot(taiwan_map) +
    geom_sf(aes(fill = First_place, color = second_color), lwd = .1) +
    coord_sf(
        xlim = c(118, 124),
        ylim = c(21.5, 26.5),
        expand = FALSE
    ) +
    theme_bw() +
    theme(panel.background = element_rect(fill = "lightblue"),
          legend.position="top")

tw_map +
    scale_fill_manual(
        values = c(
            `7-11` = color_711,
            `FamilyMart` = color_familymart,
            `Forgotten Place` = "GREY",
            `Draw [7-11, FamilyMart]` = color_7_f,
            `Draw [7-11, OK]` = color_7_o
        )
    ) +
    scale_color_manual(
        values = c(
            `7-11` = color_711,
            `familymart` = color_familymart
        )
    ) +
    labs(fill = "Leading Store") +
    guides(color = FALSE)
ggsave("test.png")
