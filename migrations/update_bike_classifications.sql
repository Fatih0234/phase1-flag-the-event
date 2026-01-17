-- Bike Classification Results Update
-- Generated: 2026-01-16T23:59:12.259431
-- Total predictions: 118

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Radweg sehr verengt Unfall gefahr'],
    bike_reasoning = 'Der Text erwähnt explizit einen ''Radweg'', der verengt ist und eine ''Unfallgefahr'' darstellt, was auf eine Beeinträchtigung der Radinfrastruktur hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '1-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Ampel liegt kaputt auf dem Boden, rundherum sind Scherben'],
    bike_reasoning = 'Der Text erwähnt Scherben und eine kaputte Ampel auf dem Boden, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '1-2026';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Als Radfahrer ist die Stelle sehr gefährlich.'],
    bike_reasoning = 'Der Text erwähnt explizit eine Gefahr für Radfahrer an der beschriebenen Stelle, was auf eine Relevanz für den Radverkehr hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10-2026';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Abstehende Gehwegplatten'],
    bike_reasoning = 'Der Text beschreibt eine defekte Oberfläche auf dem Gehweg, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radverkehrssicherheit, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '100-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['Kreuzung Schlagbaumsweg/Feldweg Ostmerheimer Str.'],
    bike_reasoning = 'Der Text beschreibt eine Müllablagerung an einer Kreuzung, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10000-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Eine Abbiegespur nach links auf den Clevischen Ring gesperrt, aber (seit Jahren) keine Baustelle? Jeden Morgen Rückstau!'],
    bike_reasoning = 'The text describes a traffic jam due to a closed turning lane, but does not mention any specific bike infrastructure or bike-related safety concerns.',
    bike_classification_date = NOW()
WHERE service_request_id = '10001-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'AWB Fahrzeug machen hier auf dem Strandstreilen Pause'],
    bike_reasoning = 'The report describes illegal dumping of trash and vehicles taking breaks on a beach area, with no mention of bike infrastructure or bike-related safety concerns.',
    bike_classification_date = NOW()
WHERE service_request_id = '10002-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['wilder Müll'],
    bike_reasoning = 'Der Text beschreibt wilden Müll auf einer Grünfläche, was keine explizite Relevanz für den Radverkehr oder die Radinfrastruktur aufweist.',
    bike_classification_date = NOW()
WHERE service_request_id = '10003-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Defekte Verkehrszeichen', 'Aus dem Boden rausgehoben'],
    bike_reasoning = 'Der Text erwähnt defekte Verkehrszeichen, die aus dem Boden gehoben wurden, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10008-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'Müll abgestellt'],
    bike_reasoning = 'Der Text beschreibt das Problem von wildem Müll, was keine explizite Relevanz für den Radverkehr oder die Rad-Infrastruktur aufweist.',
    bike_classification_date = NOW()
WHERE service_request_id = '1001-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['Der Bordstein ist komplett lose und stellt eine Stolperfalle dar'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit einer losen Bordsteinkante, die eine Stolperfalle darstellt, aber es gibt keine expliziten Wörter oder visuellen Marker, die auf Radverkehrsinfrastruktur hindeuten.',
    bike_classification_date = NOW()
WHERE service_request_id = '1001-2026';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Sperrmüll auf dem Geweg'],
    bike_reasoning = 'Der Begriff ''Geweg'' ist nicht explizit als Radweg oder Geh- und Radweg klassifiziert, und ''Sperrmüll'' ist kein direkter Indikator für Radverkehrsrelevanz.',
    bike_classification_date = NOW()
WHERE service_request_id = '10010-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['Hochstehende Gehwegplatten', 'Hier Unfall Gefahr'],
    bike_reasoning = 'Der Text beschreibt eine Stolperkante durch hochstehende Gehwegplatten und eine damit verbundene Unfallgefahr, aber es gibt keine expliziten Erwähnungen von Radwegen, Radfahrstreifen oder anderen radspezifischen Infrastrukturelementen.',
    bike_classification_date = NOW()
WHERE service_request_id = '10012-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Der Weg hier wird schon seit Wochen nicht gereinigt'],
    bike_reasoning = 'Der Text erwähnt einen Weg, der nicht gereinigt wird, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radverkehr, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10013-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Es hängt noch immer ein AfD Wahlplakat.'],
    bike_reasoning = 'The text mentions a political poster, which is a social/advertising content without any explicit reference to bike infrastructure or bike traffic safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10014-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Schrottroller', 'FIN negativ'],
    bike_reasoning = 'Der Text beschreibt einen Schrottroller und eine negative FIN-Prüfung, was auf ein privates oder soziales Thema ohne Bezug zur Radinfrastruktur hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10015-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'Gegenüber der Evastr 25 Katharinenpforte'],
    bike_reasoning = 'Der Text beschreibt "Wilden Müll" an einer Adresse, was kein expliziter Bezug zu Radinfrastruktur oder Radverkehrssicherheit ist.',
    bike_classification_date = NOW()
WHERE service_request_id = '10016-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Bauschutt im Gebüsch am Weg'],
    bike_reasoning = 'Der Text erwähnt Bauschutt am Weg, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radverkehrssicherheit, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10017-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['etwas Bauschutt am Wegübergang'],
    bike_reasoning = 'Der Begriff ''Wegübergang'' ist nicht spezifisch genug, um eine Fahrradrelevanz eindeutig zu bestimmen, und es fehlen explizite Rad-Infrastruktur-Begriffe oder -Marker.',
    bike_classification_date = NOW()
WHERE service_request_id = '10018-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Nach dem Rückschnitt des Bahnhangs taucht leider überall Müll auf.'],
    bike_reasoning = 'The text describes general littering after landscaping and does not mention any specific bike infrastructure or bike-related safety concerns.',
    bike_classification_date = NOW()
WHERE service_request_id = '10019-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'Müll abgestellt'],
    bike_reasoning = 'Der Text beschreibt das Problem von wildem Müll, was keine explizite Relevanz für den Radverkehr oder die Radinfrastruktur hat.',
    bike_classification_date = NOW()
WHERE service_request_id = '1002-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Ziegelsteine Spachtelmasse Müll fast an der ganzen August-Haas-Straße'],
    bike_reasoning = 'Der Text beschreibt Müll und Ziegelsteine auf der Straße, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '1002-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['dort befinden sich Müllsäcke'],
    bike_reasoning = 'Der Text beschreibt Müllsäcke, was kein expliziter Beleg für Radverkehrsinfrastruktur oder -sicherheit ist und somit als nicht bike-relevant eingestuft wird.',
    bike_classification_date = NOW()
WHERE service_request_id = '10020-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Garten-Bauschutt vermutlich aus der Schrebergartenanlage links am Weg', 'ca. 20m weiter rechts ein altes Pflanzgefäß im Gebüsch'],
    bike_reasoning = 'Der Text beschreibt Müll auf einer Verkehrsfläche, aber es gibt keine expliziten Wörter, die auf Rad-Infrastruktur oder Radverkehr hindeuten.',
    bike_classification_date = NOW()
WHERE service_request_id = '10021-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Sperr- und anderer Müll angelehnt und -gehäuft'],
    bike_reasoning = 'Der Text beschreibt Müllablagerungen im öffentlichen Raum, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10023-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Das Loch zwischen Bahnhof Mülheim und der U-Bahn Station ist sogar noch tiefer geworden.'],
    bike_reasoning = 'Der Text beschreibt ein Loch auf einer Verkehrsfläche, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radfahrende, was eine Klassifizierung als ''uncertain'' bedingt.',
    bike_classification_date = NOW()
WHERE service_request_id = '10024-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Im Wohnviertel rund um die Artilleriestraße sind viel zu wenig Parkplätze für die Anwohner*innen.', 'Es gibt ausserdem ständig (ortsfremde) PKWs und Motorräder die zusätzlich den Anwohner*innen den Parkraum nehmen.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit Parkplätzen und Falschparkern im Wohnviertel, erwähnt aber keine spezifische Rad-Infrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10029-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Hier liegen Pöller.'],
    bike_reasoning = 'Der Begriff ''Pöller'' ist nicht explizit in den Kriterien für ''true'' aufgeführt und kann sich auf verschiedene Arten von Barrieren beziehen, die nicht spezifisch für Radfahrer sind.',
    bike_classification_date = NOW()
WHERE service_request_id = '1003-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Feuerwerk Plastikstuhl'],
    bike_reasoning = 'The description mentions ''Feuerwerk'' (fireworks) and ''Plastikstuhl'' (plastic chair), which are not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '1003-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll auf einem kleinen Grünstreifen'],
    bike_reasoning = 'The description mentions ''wilder Müll'' (illegal dumping) on a ''Grünstreifen'' (green strip), which does not explicitly relate to bike infrastructure or the safety/accessibility of bike traffic.',
    bike_classification_date = NOW()
WHERE service_request_id = '10030-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Kfz-Ampel defekt', 'Die Ampel von der Ostmerheimer Straße ist um 90Grad verdreht.'],
    bike_reasoning = 'The report mentions a defective traffic light for cars and its orientation, but provides no explicit evidence related to bike infrastructure, bike riders, or specific bike safety concerns.',
    bike_classification_date = NOW()
WHERE service_request_id = '10036-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Mehrere Schlaglöcher vom Niehler Ei aus kommend Richtung Autobahn A1. Rechte Spur'],
    bike_reasoning = 'Der Text beschreibt Schlaglöcher auf einer Fahrspur, aber es gibt keine expliziten Begriffe, die auf Radverkehrsinfrastruktur oder Radfahrende hindeuten, was für eine Klassifizierung als ''true'' notwendig wäre.',
    bike_classification_date = NOW()
WHERE service_request_id = '1004-2026';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Kinder mit ihren Rollern verhakt und sind gestürzt'],
    bike_reasoning = 'Der Text beschreibt Stürze von Kindern mit Rollern aufgrund einer defekten Oberfläche, aber es gibt keine expliziten Erwähnungen von Radwegen, Radfahrstreifen oder anderen radspezifischen Infrastrukturen, die eine Einstufung als ''true'' rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10040-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Altkleider im Wald abgelegt.', 'Am Waldweg neben dem asphaltierten Weg parallel zur A1 in Heimersdorf.'],
    bike_reasoning = 'Der Text beschreibt illegale Müllentsorgung (Altkleider) und Hindernisse (Baumstamm) auf einem Waldweg, ohne explizite Erwähnung von Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10041-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Die Gehwegplatten stehen hoch und sind lose.', 'Stolpergefahr.'],
    bike_reasoning = 'Der Text beschreibt eine Stolpergefahr auf dem Gehweg aufgrund defekter Gehwegplatten, aber es gibt keine expliziten Erwähnungen von Radinfrastruktur oder Radverkehr, die eine Einstufung als ''true'' rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10044-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['In der Zufahrt zur Weide liegen Laminatbretter.'],
    bike_reasoning = 'The description mentions laminate boards in a driveway, which is not related to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10045-2025';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Der ehemalige Radweg auf der Dürener Straße ist kein ausgewiesener Radweg mehr.', 'Dennoch fahren alle Fahrradfahrer nicht über die Straße, sondern über den alten Radweg.'],
    bike_reasoning = 'Der Text erwähnt explizit einen ''ehemaligen Radweg'' und das Verhalten von ''Fahrradfahrern'' auf diesem, was auf eine Relevanz für den Radverkehr hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10046-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['massive Schäden vorhanden', 'E-Busse und Schwerlastverkehr durch die Straße rasen'],
    bike_reasoning = 'Der Text beschreibt massive Straßenschäden durch Schwerlastverkehr, aber es gibt keine expliziten Erwähnungen von Radinfrastruktur oder Radfahrenden, die eine Bike-Relevanz eindeutig belegen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10047-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Der Bürgersteig hat an mehrere Stellen Schlaglöcher.'],
    bike_reasoning = 'Der Text erwähnt Schlaglöcher auf dem Bürgersteig, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radverkehr, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10048-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Hier sind mehrere ziemlich tiefe Löcher.', 'Werden immer größer, ist ja eine Straße, durch die sehr viele Autos fahren.'],
    bike_reasoning = 'Der Text beschreibt tiefe Löcher auf einer Straße, was ein allgemeines Verkehrsproblem darstellt, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radfahrende, die von diesem Problem betroffen wären.',
    bike_classification_date = NOW()
WHERE service_request_id = '10049-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Sperrmüll am Baum'],
    bike_reasoning = 'The description mentions ''Sperrmüll am Baum'' which refers to bulky waste near a tree, not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '1005-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Immer wieder wird an diesen Containern wilder Müll abgelegt.', 'Kann man dort nicht Hinweisschilder mit Verweis auf die AWB Sammelstelle in Gremberghoven aufstellen und ggf sogar eine Kamera installieren?'],
    bike_reasoning = 'Der Text beschreibt illegale Müllentsorgung bei Containern, was kein Thema des öffentlichen Radverkehrs ist.',
    bike_classification_date = NOW()
WHERE service_request_id = '1005-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Auf dem Parkplatz steht seit einigen Tagen ein Fahrzeug ohne Nummernschild.'],
    bike_reasoning = 'The description mentions a vehicle on a parking lot, which is not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '10051-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['gefährdendes Schild', 'mit Fahrrad dagegen fahren'],
    bike_reasoning = 'Der Text erwähnt ein gefährdendes Schild und die Möglichkeit, damit gegen ein Fahrrad zu fahren, was auf eine potenzielle Gefahr für Radfahrende hindeutet, aber es gibt keine explizite Erwähnung von Radinfrastruktur oder spezifischen Radverkehrsmarkierungen.',
    bike_classification_date = NOW()
WHERE service_request_id = '10052-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY[],
    bike_reasoning = 'Der Text erwähnt keine expliziten Rad-Infrastruktur-Begriffe oder visuelle Marker, die auf Radverkehr hindeuten, und beschreibt lediglich allgemeine Straßenbauarbeiten und Stau.',
    bike_classification_date = NOW()
WHERE service_request_id = '10055-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['autoreifen die bei putzmunter gefunden wurden'],
    bike_reasoning = 'The text mentions finding car tires, which is not related to bicycle infrastructure or the use of bicycles in public spaces.',
    bike_classification_date = NOW()
WHERE service_request_id = '10056-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['toilettenschüssel vor der brücke rechts'],
    bike_reasoning = 'Die Beschreibung erwähnt eine Toilettenschüssel vor einer Brücke, was keinen Bezug zu Radinfrastruktur oder Radverkehr hat.',
    bike_classification_date = NOW()
WHERE service_request_id = '10057-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['gerümpel auf dem gehweg'],
    bike_reasoning = 'The description mentions ''gerümpel auf dem gehweg'' which translates to ''junk on the sidewalk'', and does not contain any explicit terms related to bike infrastructure or bike traffic safety, thus it is classified as non-bike-related.',
    bike_classification_date = NOW()
WHERE service_request_id = '10058-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Metallstangen'],
    bike_reasoning = 'The description mentions ''Metallstangen'' (metal poles) which could be an obstruction on a traffic surface, but there is no explicit mention of bike infrastructure or bike-related safety issues.',
    bike_classification_date = NOW()
WHERE service_request_id = '1006-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Ein alter Maibaum, Straßenpöller und sonstiger Müll'],
    bike_reasoning = 'Der Text beschreibt Müll und Hindernisse im öffentlichen Raum, aber es gibt keine expliziten Erwähnungen von Radinfrastruktur oder Radverkehrssicherheit, was ihn nicht bike-relevant macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10060-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Ecke Wilhelm-Schlombs-Allee liegt Sperrmüll.'],
    bike_reasoning = 'The report mentions ''Sperrmüll'' (bulky waste) at a street corner, which is not related to bike infrastructure or the safety/accessibility of cyclists.',
    bike_classification_date = NOW()
WHERE service_request_id = '10063-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Mehrere Standfüsse bitte abholen'],
    bike_reasoning = 'The text mentions picking up ''Standfüsse'' which are likely traffic cones or similar temporary barriers, and does not contain any explicit terms related to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10064-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['defekten Gullideckel', 'Nach der Unterführung auf der linken Seite befindet er sich.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit einem defekten Gullideckel auf einem Weg, aber es gibt keine expliziten Wörter, die auf Rad-Infrastruktur oder Radverkehr hindeuten.',
    bike_classification_date = NOW()
WHERE service_request_id = '10065-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Gully verstopft'],
    bike_reasoning = 'The report mentions a clogged gully, which is a general infrastructure issue and not explicitly related to bike infrastructure or safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10067-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['wilder Müll'],
    bike_reasoning = 'The report mentions ''wilder Müll'' (illegal dumping) under an autobahn bridge, which is not related to bike infrastructure or the use of bikes in public spaces.',
    bike_classification_date = NOW()
WHERE service_request_id = '10068-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Am Rendsburger Platz hängt an einer Laterne gegenüber der Esso-Tankstelle (Ecke Pfälzischer Ring, auf der Seite der Grünanlage) noch immer ein Wahlplakat der AfD.'],
    bike_reasoning = 'The text describes a political poster hanging on a lamppost, which is not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '10069-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['keine Müllentsorgung'],
    bike_reasoning = 'The report discusses a lack of waste disposal, which is not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '1007-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Unfassbare Mengen an Müll und Unrat entlang der gesamten Straße!', 'Jetzt auch noch wildcamper dazu.'],
    bike_reasoning = 'Der Text beschreibt Müll und Wildcamper entlang einer Straße, ohne explizite Erwähnung von Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10070-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilde Müllentsorgung auf der Bernhard-Günther-Straße in Merkenich, des Weiteren stehen in der Straße 3 alte Wohnwagen in denen jemand haust, und die rundherum auch vermüllt sind.'],
    bike_reasoning = 'Der Text beschreibt wilde Müllentsorgung und Wohnwagen auf einer Straße, aber es gibt keine expliziten Erwähnungen von Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10071-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Kfz-Ampel defekt', 'Rotlicht an der unteren Ampel der WDR Ausfahrt defekt'],
    bike_reasoning = 'The report explicitly mentions a defective vehicle traffic light and a broken red light at the WDR exit, with no mention of bicycle infrastructure or specific issues related to cyclists.',
    bike_classification_date = NOW()
WHERE service_request_id = '10072-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'Wieder Müll'],
    bike_reasoning = 'The report mentions ''wilden Müll'' and ''Müll'', which are general waste issues and not related to bike infrastructure or bike traffic safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10073-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['eine Baustelle für den Neubau eines Sinkkastens eingerichtet', 'ein Loch auf dem Gehweg', 'der Gehwegasphalt bricht immer weiter aus (Stolper -und Unfallgefahr)'],
    bike_reasoning = 'Der Text beschreibt ein Loch und bröckligen Gehwegasphalt mit Stolper- und Unfallgefahr, aber es gibt keine expliziten Erwähnungen von Radwegen, Radfahrstreifen oder anderen radspezifischen Infrastrukturelementen, die eine TRUE-Klassifizierung rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10074-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Fußgängerampel defekt', 'Grüne Ampel defekt'],
    bike_reasoning = 'The report mentions a defective pedestrian traffic light and a defective green light, with no explicit mention of bike infrastructure or bike-related safety concerns.',
    bike_classification_date = NOW()
WHERE service_request_id = '10076-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['illegal entsorgten Metallfahrradständer', 'Fahrradständer ständig voll wegen Dauerparkern'],
    bike_reasoning = 'Der Fahrradständer ist ein Objekt und seine Belegung oder sein Verbleib hat keinen direkten Bezug zur Radverkehrsinfrastruktur oder Sicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10077-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['2 Schilderfüße'],
    bike_reasoning = 'The description mentions ''2 Schilderfüße'' (2 sign bases), which does not provide explicit evidence of bike-related infrastructure or issues.',
    bike_classification_date = NOW()
WHERE service_request_id = '1008-2026';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Auf der linken Spur gibt es großflächige Asphaltschäden'],
    bike_reasoning = 'Der Text beschreibt großflächige Asphaltschäden auf einer Spur, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radfahrende, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10080-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Der ehemalige Radweg auf beiden Seiten der Dürener Straße wird immer noch von allen  - auch den schnellsten  - Radfahrern genutzt.', 'Es fehlen Absperrungen der ehemaligen Radwege an jeder Kreuzung.'],
    bike_reasoning = 'Der Text erwähnt ''ehemalige Radwege'' und dass diese von Radfahrern genutzt werden, was auf eine ehemalige Radinfrastruktur hindeutet, aber es gibt keine explizite Nennung aktueller Radinfrastruktur-Wörter oder visueller Marker, die eine klare TRUE-Klassifizierung rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10082-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Kfz-Ampel defekt', 'Ampel komplett heruntergerissen'],
    bike_reasoning = 'The report mentions a broken traffic light for cars, but provides no explicit evidence related to bike infrastructure or bike safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10083-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['der erst vor wenigen Wochen ausgebesserte Belag des Parkstreifens', 'Aufwerfungen und Gräben'],
    bike_reasoning = 'Der Text beschreibt eine defekte Oberfläche mit Aufwerfungen und Gräben auf einem Parkstreifen, ohne explizite Erwähnung von Radwegen oder Radverkehrsmarkierungen.',
    bike_classification_date = NOW()
WHERE service_request_id = '10085-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll'],
    bike_reasoning = 'The report mentions ''wilder Müll'' (littering) without any explicit reference to bike infrastructure, bike riders, or safety concerns related to cycling, thus it is not bike-related.',
    bike_classification_date = NOW()
WHERE service_request_id = '10087-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Alte Matratze'],
    bike_reasoning = 'Die Beschreibung einer alten Matratze bezieht sich auf Müll und nicht auf die Radinfrastruktur oder den Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '10089-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['fiese Matratze'],
    bike_reasoning = 'The description mentions a mattress, which is considered ''wild trash'' and does not relate to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10091-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll'],
    bike_reasoning = 'The report mentions ''wilder Müll'' which refers to illegal dumping and does not contain any explicit evidence related to bike infrastructure, bike traffic, or safety concerns for cyclists.',
    bike_classification_date = NOW()
WHERE service_request_id = '10092-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'irgendein Schrott'],
    bike_reasoning = 'Der Text beschreibt ''wilden Müll'' und ''Schrott'', was keine explizite Verbindung zum Radverkehr oder zur Radinfrastruktur herstellt.',
    bike_classification_date = NOW()
WHERE service_request_id = '10093-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Ampel für die Dürener Str', 'Mommsenstraße, Kitschburgerstr. und Decksteinerstr. hatten Dauerrot'],
    bike_reasoning = 'Der Text beschreibt eine Ampelstörung, die den gesamten Kreuzungsbereich betrifft, aber es gibt keine expliziten Hinweise auf Radverkehrsinfrastruktur oder spezifische Probleme für Radfahrende.',
    bike_classification_date = NOW()
WHERE service_request_id = '10094-2025';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Erhöhte Unfall Gefahr durch ausweichen und durch Radverkehr des anliegenden Kindergartens.'],
    bike_reasoning = 'Der Text erwähnt explizit Radverkehr im Kontext einer Gefahrensituation, was auf eine Relevanz für die Radinfrastruktur hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10095-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Holzplatten abgeladen.'],
    bike_reasoning = 'The description mentions ''Holzplatten abgeladen'' which refers to dumped waste and not to any bike-related infrastructure or activity.',
    bike_classification_date = NOW()
WHERE service_request_id = '10099-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['diverser Sperrmüll'],
    bike_reasoning = 'The description mentions ''diverser Sperrmüll'' (various bulky waste) next to a gallery, which is not related to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '101-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Ist ja schön wenn einer den Feuerwerksabfall wieder aufhebt', 'Aber ich finde es eine Frechheit ihn dann hier zu entsorgen'],
    bike_reasoning = 'Der Text beschreibt das Entsorgen von Feuerwerksabfällen und Müll, was keine explizite Relevanz für den Radverkehr oder die Radinfrastruktur aufweist.',
    bike_classification_date = NOW()
WHERE service_request_id = '101-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Müllbehälter quillt über mit Hundekottüten', 'Müllbehälter bereits längere Zeit nicht geleert'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit überquellenden Müllbehältern und Hundekottüten, was keine explizite Rad-Infrastruktur oder Radverkehrssicherheit betrifft.',
    bike_classification_date = NOW()
WHERE service_request_id = '1010-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Schlagloch Innere Kanalstraße Linksabbieger in Richtung Telekom Gebäude'],
    bike_reasoning = 'Der Text beschreibt ein Schlagloch auf einer Straße, aber es gibt keine expliziten Hinweise auf Radinfrastruktur oder Radverkehrssicherheit, die eine Einstufung als ''true'' rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10100-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Schlagloch'],
    bike_reasoning = 'The report mentions a ''Schlagloch'' (pothole) on the surface, which is a general issue on a traffic area and not explicitly related to bike infrastructure or safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10101-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['„Wilder Aschenbecher“ voll Kippen auf dem Boden vor der Fassade.'],
    bike_reasoning = 'Der Text beschreibt Müll (Kippen) vor der Fassade eines Gebäudes und enthält keine expliziten Hinweise auf Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10102-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Seit gestern, 8.4. liegt wieder ein gelber Sack an der Baumscheibe des Hauses Adolphstraße 46.', 'Das zieht Ratten und Mäuse an und verschandelt die Straße optisch.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit Müll und dessen Entsorgung im öffentlichen Raum, hat aber keinen Bezug zu Radinfrastruktur oder Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '10103-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Der städt. Mülleimer, der auf der Grünfläche vor der KiTa stand, ist verschwunden.', 'Müll und Hundekottüten jetzt in der Wiese liegen.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit Müll auf einer Grünfläche, das keine explizite Rad-Infrastruktur oder Radverkehrssicherheit betrifft.',
    bike_classification_date = NOW()
WHERE service_request_id = '10104-2025';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Mit dem Fahrrad eine absolute Zumutung da die Autos im Berufsverkehr überhaupt keine Rücksicht nehmen.'],
    bike_reasoning = 'Der Text beschreibt eine Situation, die für Radfahrende eine Zumutung darstellt, was auf eine Beeinträchtigung des Radverkehrs hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10108-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Die Radfahrer halten nicht am Zebrastreifen sondern fahren einfach drüber.', 'Fußgänger die in den Waidmarkt abbiegen wollen müssen nicht nur auf Autos sondern jetzt auch auf Radfahrer achten die den Zebrastreifen einfach überqueren ohne auf die Fußgänger zu achten.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit Radfahrern, die Zebrastreifen überqueren, aber es gibt keine explizite Erwähnung von Radinfrastruktur wie Radwegen oder Radfahrstreifen, was für eine TRUE-Klassifizierung erforderlich wäre.',
    bike_classification_date = NOW()
WHERE service_request_id = '10109-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wegen diesen Restmüll Haufen laufen viele Ratten rum.', 'wir nutzen den Weg sehr oft, weil durch die GarageGang kommt man an den Spielplatz'],
    bike_reasoning = 'Der Text beschreibt ein Müllproblem und dessen Auswirkungen auf die Gesundheit und die Nutzung eines Weges, der zu einem Spielplatz führt, aber es gibt keine expliziten Erwähnungen von Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10110-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Ragt sehr weit auf den Gehweg man kommt schlecht drum herum.'],
    bike_reasoning = 'Der Text beschreibt ein Hindernis auf dem Gehweg, das die Passierbarkeit einschränkt, aber es gibt keine expliziten Begriffe, die auf Radverkehrsinfrastruktur oder Radfahrende hindeuten.',
    bike_classification_date = NOW()
WHERE service_request_id = '10112-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Diese Baustellenschilder + Gewichte (siehe Bild hinten) liegen seit Wochen in unserer Straße.... Bitte abholen.'],
    bike_reasoning = 'Der Text beschreibt Baustellenschilder und Gewichte, die in einer Straße liegen und abgeholt werden sollen, ohne jeglichen Bezug zu Radwegen, Radfahrstreifen oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10114-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 1.0,
    bike_evidence = ARRAY['Wilder Müll', 'bitte den Müll beseitigen'],
    bike_reasoning = 'Der Text beschreibt das Problem von wildem Müll und bittet um dessen Beseitigung, ohne jeglichen Bezug zu Radinfrastruktur oder Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '10117-2025';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Hinweis Radverkehr in beide Richtungen', 'blaue Fuß-Radwegschilder'],
    bike_reasoning = 'Der Text erwähnt explizit Schilder, die auf Radverkehr hinweisen (''Hinweis Radverkehr in beide Richtungen'') und ''Fuß-Radwegschilder'', was auf eine relevante Radinfrastruktur hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10118-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Seit Silvester nicht geleerter Mülleimer.', 'Hundekotbeutel liegen in der Natur drumherum.'],
    bike_reasoning = 'Der Text beschreibt ein Müllproblem mit Mülleimern und Hundekotbeuteln im Park, was keine explizite Rad-Infrastruktur oder Radverkehrssicherheit betrifft.',
    bike_classification_date = NOW()
WHERE service_request_id = '1012-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Schlagloch'],
    bike_reasoning = 'Der Text erwähnt ein Schlagloch auf der Fahrspur im Randbereich, aber es gibt keine expliziten Wörter, die auf eine Rad-Infrastruktur oder Radfahrende hindeuten, was für eine TRUE-Klassifizierung erforderlich wäre.',
    bike_classification_date = NOW()
WHERE service_request_id = '1012-2026';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Defekter Kanaldeckel der klappert wenn ein Fahrzeug darüber fährt.'],
    bike_reasoning = 'Der Text beschreibt ein Problem mit einem Kanaldeckel, der auf der Fahrbahn klappert, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radfahrende, was eine Klassifizierung als ''true'' oder ''false'' unsicher macht.',
    bike_classification_date = NOW()
WHERE service_request_id = '10120-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['große Schlaglöcher auf der Straße', 'fliegen Steine durch die Gegend'],
    bike_reasoning = 'Der Text beschreibt Schlaglöcher und herumfliegende Steine auf einer Straße, was zwar ein Problem darstellt, aber keine explizite Rad-Infrastruktur oder Radverkehrssicherheit erwähnt.',
    bike_classification_date = NOW()
WHERE service_request_id = '10121-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll', 'liegt bereits seid 1 woche da'],
    bike_reasoning = 'Der Text beschreibt illegale Müllentsorgung, was kein Thema des Radverkehrs ist.',
    bike_classification_date = NOW()
WHERE service_request_id = '10122-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Sperrmüll (Schrank, Teppich)'],
    bike_reasoning = 'The description mentions bulky waste like a cabinet and carpet, which is not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '10123-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['dort wo der Fuß-, Radweg endet in der Nähe der Glascontainer'],
    bike_reasoning = 'Der Text erwähnt einen ''Fuß-, Radweg'', was auf eine Fahrrad-Infrastruktur hindeutet, aber die Beschreibung des Problems (Müll) und die genaue Lage (Ende des Weges) sind nicht spezifisch genug, um eine klare Relevanz für den Radverkehr zu bestätigen.',
    bike_classification_date = NOW()
WHERE service_request_id = '10125-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['2 Mülltüten am Straßenrand'],
    bike_reasoning = 'Der Text beschreibt Müll am Straßenrand, was kein expliziter Beleg für Radverkehrsinfrastruktur oder Radverkehrssicherheit ist.',
    bike_classification_date = NOW()
WHERE service_request_id = '10127-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['an den Glascontainern Ecke Esenbeckstraße/Brehmstraße wilder Müll abgelegt'],
    bike_reasoning = 'Der Text beschreibt illegale Müllablagerung bei Glascontainern und enthält keine expliziten Hinweise auf Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '10130-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Im Kreisel liegt Müll'],
    bike_reasoning = 'Der Text erwähnt Müll auf einer Verkehrsfläche (Kreisel), aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehrssicherheit, die eine Einstufung als ''true'' rechtfertigen würden.',
    bike_classification_date = NOW()
WHERE service_request_id = '10131-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.8,
    bike_evidence = ARRAY['Großes, tiefes Schlagloch auf der Straße'],
    bike_reasoning = 'Der Text beschreibt ein Schlagloch auf der Straße, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radfahrende, was eine Klassifizierung als ''uncertain'' bedingt.',
    bike_classification_date = NOW()
WHERE service_request_id = '10132-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.6,
    bike_evidence = ARRAY['Undefinierbarer Fleck ( eventuell von Mietroller/Batterieflüssigkeit?) Riecht merkwürdig.'],
    bike_reasoning = 'Der Text beschreibt einen Fleck auf der Oberfläche, der möglicherweise von einem Mietroller stammt, aber es gibt keine expliziten Hinweise auf Rad-Infrastruktur oder Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '10135-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Die Ampel in Köln Mülheim. Frankfurter Str gegenüber Ackerstr. hat eine zu kurze Grünzeit.'],
    bike_reasoning = 'The text mentions an issue with an traffic light''s green time but does not explicitly mention any bike-related infrastructure or safety concerns for cyclists.',
    bike_classification_date = NOW()
WHERE service_request_id = '10138-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Im Rosengarten liegen noch große Mengen Müll von Silvester.'],
    bike_reasoning = 'Der Text beschreibt Müll im Rosengarten, ohne jeglichen Bezug zu Radwegen, Radfahrstreifen oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '1014-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Vor dem Container, Kurfürstenstraße 17 wird sonstiger Müll entsorgt.'],
    bike_reasoning = 'The report describes illegal dumping of general waste near a container, which is not related to bike infrastructure or cycling.',
    bike_classification_date = NOW()
WHERE service_request_id = '1014-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Vor dem Moscheeverein liegt eine alte Matratze.'],
    bike_reasoning = 'Die Meldung beschreibt Müll (eine Matratze) vor einem Gebäude, ohne jeglichen Bezug zu Radinfrastruktur oder Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '10146-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Picknickcontainer i.H. Wetterpilz in Westhoven'],
    bike_reasoning = 'The request is about placing a picnic container to prevent illegal dumping, which is not related to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10149-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Müll Parkplatz am Fußballplatz in Rodenkirchen, Konrad-Adenauer-strasse'],
    bike_reasoning = 'Der Text beschreibt wilden Müll auf einem Parkplatz und enthält keine expliziten Bezüge zu Radinfrastruktur oder Radverkehrssicherheit.',
    bike_classification_date = NOW()
WHERE service_request_id = '1015-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Auf dem Gehweg vor dem Grundstück Erpeler Str. 32 haben sich mehrere Gehwegplatten gelöst und sind gerissen.', 'Die Kanten bilden Stolperstellen und sind ein Hindernis für Menschen mit Einschränkungen (Blinde, Gehbehinderung).'],
    bike_reasoning = 'Der Text beschreibt Probleme mit Gehwegplatten auf einem Gehweg, ohne jegliche Erwähnung von Radwegen, Radfahrstreifen oder Radverkehr.',
    bike_classification_date = NOW()
WHERE service_request_id = '1015-2026';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Alter zerlegter Motorroller, Abfall im ges. Bereich und am Zaun'],
    bike_reasoning = 'Der Text beschreibt Müll und einen zerlegten Motorroller, was keine explizite Rad-Infrastruktur oder Radverkehrssicherheit betrifft.',
    bike_classification_date = NOW()
WHERE service_request_id = '10150-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Müll, Reifen, Farbdosen'],
    bike_reasoning = 'The description mentions ''Müll, Reifen, Farbdosen'' which are general waste items and do not explicitly refer to bike infrastructure or bike-related safety/accessibility issues in public spaces.',
    bike_classification_date = NOW()
WHERE service_request_id = '10151-2025';

UPDATE events SET
    bike_related = TRUE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Radfahrampel am Neumarkt, Ecke Richmodstraße ist zu niedrig angebracht', 'Radfahrer übersehen die Ampel'],
    bike_reasoning = 'Der Text erwähnt explizit eine defekte Radfahrampel und beschreibt Konflikte, die durch deren Positionierung entstehen, was auf eine Relevanz für den Radverkehr hindeutet.',
    bike_classification_date = NOW()
WHERE service_request_id = '10152-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Wilder Renovierungsmüll'],
    bike_reasoning = 'The description ''Wilder Renovierungsmüll'' does not contain any explicit terms related to bike infrastructure, bike users, or traffic safety, nor does it describe a problem on a designated bike path or lane.',
    bike_classification_date = NOW()
WHERE service_request_id = '10153-2025';

UPDATE events SET
    bike_related = NULL,
    bike_confidence = 0.7,
    bike_evidence = ARRAY['Die Fahrbahnrand ist auf der linken Seite in Richtung südwest in Höhe Mottenkaul 18f (direkt gegenüber) auf einer Größe von ca. 80cm Durchmesser beschädigt.', 'Asphaltbrocken fliegen während der Durchfahrt auf die Straße und gegen parkende Autos.'],
    bike_reasoning = 'Der Text beschreibt eine beschädigte Fahrbahn und herumfliegende Asphaltbrocken, was ein allgemeines Verkehrsproblem darstellt, aber keine explizite Rad-Infrastruktur oder Radverkehrssicherheit erwähnt.',
    bike_classification_date = NOW()
WHERE service_request_id = '10154-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['Haufen von Sperrmüll mit Abfall', 'Heckhofweg'],
    bike_reasoning = 'The report describes piles of bulky waste and trash on the street, which is not related to bike infrastructure or cycling safety.',
    bike_classification_date = NOW()
WHERE service_request_id = '10158-2025';

UPDATE events SET
    bike_related = FALSE,
    bike_confidence = 0.9,
    bike_evidence = ARRAY['sehr viel Wilder Müll im Grünstreifen', 'Teilweise auch Sondermüll'],
    bike_reasoning = 'Der Text beschreibt illegale Müllentsorgung in einem Grünstreifen und erwähnt keine Rad-Infrastruktur oder Radverkehrsprobleme.',
    bike_classification_date = NOW()
WHERE service_request_id = '10159-2025';
