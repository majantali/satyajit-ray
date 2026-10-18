
## read in data

actors <- read.csv("satyajit_ray_actors.csv", stringsAsFactors = FALSE)[c(1, 2, 4)]
actors <- subset(actors, trimws(actor) != "")
str(actors)

## For now, only keep actors who appear in at least two films

atab <- table(actors$actor)
keep.actors <- names(atab)[atab > 1]

actors <- subset(actors, actor %in% keep.actors)
actors <- actors[order(actors$actor), ]

actors[c(3, 1, 2)]

photo.name <- function(actor, year, film)
{
    actor <- gsub(" ", "_", actor, fixed = TRUE)
    film <- gsub(" ", "_", film, fixed = TRUE)
    sprintf("%s__%d__%s.jpg", actor, year, film)
}



filenames <- with(actors, # subset(actors, year %in% c(1955, 1958, 1962, 1966, 1967, 1971, 1974, 1975, 1978)), 
                  photo.name(actor, year, film))



## make placeholders (to be replaced by actual photos)
for (f in filenames)
{
    f <- file.path("photos", f)
    if (!file.exists(f)) file.create(f)
    cat(f, " -> ", file.size(f), fill = TRUE)
}




## The next step is to fill in as many as possible with photos. Once
## this is done, we need to think about how to "visualize" them

. <- function(e) {
    s <- substitute(e)
    function(.) {
        eval(s)
    }
}

actors$file.paths <- file.path("photos", with(actors, photo.name(actor, year, film)))
actors$photo.available <- sapply(actors$file.paths, .(file.exists(.) && file.size(.) > 0))

actors.available <- subset(actors, photo.available)


## make adjacency matrix

adj <- 
    with(actors.available,
    {
        year.film <- paste(year, film)
        ## str(year.film)
        ufilm <- unique(film)
        uactor <- unique(actor)
        a <- matrix(NA_character_, nrow = length(ufilm), ncol = length(uactor))
        ## str(a)
        rownames(a) <- sort(unique(year.film))
        colnames(a) <- names(sort(table(actor), decreasing = TRUE))
        for (i in seq_along(year.film))
        {
            ## cat(sprintf("%d -> %s -> %s\n", i, year.film[i], actor[i]))
            a[year.film[i], actor[i]] <- file.paths[i]
        }
        a
    })

library(lattice)
levelplot(t(is.na(adj)), scales = list(x = list(rot = 90)), col.regions = grey.colors)
