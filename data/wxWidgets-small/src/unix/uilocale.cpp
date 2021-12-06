///////////////////////////////////////////////////////////////////////////////
// Name:        src/unix/uilocale.cpp
// Purpose:     wxUILocale implementation for Unix systems
// Author:      Vadim Zeitlin
// Created:     2021-08-01
// Copyright:   (c) 2021 Vadim Zeitlin <vadim@wxwidgets.org>
// Licence:     wxWindows licence
///////////////////////////////////////////////////////////////////////////////

// ============================================================================
// declarations
// ============================================================================

// ----------------------------------------------------------------------------
// headers
// ----------------------------------------------------------------------------

// for compilers that support precompilation, includes "wx.h".
#include "wx/wxprec.h"

#if wxUSE_INTL

#include "wx/uilocale.h"
#include "wx/private/uilocale.h"

#include "wx/unix/private/uilocale.h"

#include "wx/intl.h"

#include <locale.h>
#ifdef HAVE_LANGINFO_H
    #include <langinfo.h>
#endif

namespace
{

// ----------------------------------------------------------------------------
// wxUILocale implementation using standard Unix/C functions
// ----------------------------------------------------------------------------

class wxUILocaleImplUnix : public wxUILocaleImpl
{
public:
    // If "loc" is non-NULL, this object takes ownership of it and will free it.
    explicit wxUILocaleImplUnix(wxLocaleIdent locId
#ifdef HAVE_LOCALE_T
                               , locale_t loc = NULL
#endif // HAVE_LOCALE_T
                               );
    ~wxUILocaleImplUnix() wxOVERRIDE;

    void Use() wxOVERRIDE;

    wxString GetName() const wxOVERRIDE;
    wxString GetInfo(wxLocaleInfo index, wxLocaleCategory cat) const wxOVERRIDE;
    int CompareStrings(const wxString& lhs, const wxString& rhs,
                       int flags) const wxOVERRIDE;

private:
#ifdef HAVE_LANGINFO_H
    // Call nl_langinfo_l() if available, or nl_langinfo() otherwise.
    const char* GetLangInfo(nl_item item) const;
#endif // HAVE_LANGINFO_H

    wxLocaleIdent m_locId;

#ifdef HAVE_LOCALE_T
    // Only null for the default locale.
    locale_t m_locale;
#endif // HAVE_LOCALE_T

    wxDECLARE_NO_COPY_CLASS(wxUILocaleImplUnix);
};

#ifdef HAVE_LOCALE_T

// Simple wrapper around newlocale().
inline locale_t TryCreateLocale(const wxLocaleIdent& locId)
{
    return newlocale(LC_ALL_MASK, locId.GetName().mb_str(), NULL);
}

// Wrapper around newlocale() also trying to append UTF-8 codeset (and
// modifying its wxLocaleIdent argument if it succeeds).
locale_t TryCreateLocaleWithUTF8(wxLocaleIdent& locId)
{
    locale_t loc = TryCreateLocale(locId);
    if ( !loc && locId.GetCharset().empty() )
    {
        wxLocaleIdent locIdUTF8 = wxLocaleIdent(locId).Charset("UTF-8");
        loc = TryCreateLocale(locIdUTF8);
        if ( loc )
            locId = locIdUTF8;
    }

    return loc;
}

// Try finding a locale for the given identifier, modifying the argument to
// match the found locale if necessary.
locale_t TryCreateMatchingLocale(wxLocaleIdent& locId)
{
    locale_t loc = TryCreateLocaleWithUTF8(locId);
    if ( !loc )
    {
        // Try to find a variant of this locale available on this system: first
        // of all, using just the language, without the territory, typically
        // does _not_ work under Linux, so try adding one if we don't have it.
        if ( locId.GetRegion().empty() )
        {
            const wxString lang = locId.GetLanguage();

            const wxLanguageInfos& infos = wxGetLanguageInfos();
            for ( wxLanguageInfos::const_iterator it = infos.begin();
                  it != infos.end();
                  ++it )
            {
                const wxString& fullname = it->CanonicalName;
                if ( fullname.BeforeFirst('_') == lang )
                {
                    // We never have encoding in our canonical names, but we
                    // can have modifiers, so get rid of them if necessary.
                    const wxString&
                        region = fullname.AfterFirst('_').BeforeFirst('@');
                    if ( !region.empty() )
                    {
                        loc = TryCreateLocaleWithUTF8(locId.Region(region));
                        if ( loc )
                        {
                            // We take the first available region, we don't
                            // have enough data to know how to prioritize them
                            // (and wouldn't want to start any geopolitical
                            // disputes).
                            break;
                        }
                    }

                    // Don't bother reverting region to the old value as it will
                    // be overwritten during the next loop iteration anyhow.
                }
            }
        }
    }

    return loc;
}

#endif // HAVE_LOCALE_T

} // anonymous namespace

// ============================================================================
// implementation
// ============================================================================

wxString wxLocaleIdent::GetName() const
{
    // Construct name in the standard Unix format:
    // language[_territory][.codeset][@modifier]

    wxString name;
    if ( !m_language.empty() )
    {
        name << m_language;

        if ( !m_region.empty() )
            name << "_" << m_region;

        if ( !m_charset.empty() )
            name << "." << m_charset;

        if ( !m_modifier.empty() )
            name << "@" << m_modifier;
    }

    return name;
}

// Helper of wxSetlocaleTryAll() below which tries setting the given locale
// with and without UTF-8 suffix. Don't use this one directly.
static const char *wxSetlocaleTryUTF8(int c, const wxLocaleIdent& locId)
{
    const char *l = NULL;

    // NB: We prefer to set UTF-8 locale if it's possible and only fall back to
    //     non-UTF-8 locale if it fails.
#if wxUSE_UNICODE
    if ( locId.GetCharset().empty() )
    {
        wxLocaleIdent locIdUTF8(locId);
        locIdUTF8.Charset(wxS(".UTF-8"));

        l = wxSetlocale(c, locIdUTF8.GetName());
        if ( !l )
        {
            locIdUTF8.Charset(wxS(".utf-8"));
            l = wxSetlocale(c, locIdUTF8.GetName());
        }
        if ( !l )
        {
            locIdUTF8.Charset(wxS(".UTF8"));
            l = wxSetlocale(c, locIdUTF8.GetName());
        }
        if ( !l )
        {
            locIdUTF8.Charset(wxS(".utf8"));
            l = wxSetlocale(c, locIdUTF8.GetName());
        }
    }

    // if we can't set UTF-8 locale, try non-UTF-8 one:
    if ( !l )
#endif // wxUSE_UNICODE
        l = wxSetlocale(c, locId.GetName());

    return l;
}

// Try setting all possible versions of the given locale, i.e. with and without
// UTF-8 encoding, and with or without the "_territory" part.
const char *wxSetlocaleTryAll(int c, const wxLocaleIdent& locId)
{
    const char* l = wxSetlocaleTryUTF8(c, locId);
    if ( !l )
    {
        if ( !locId.GetRegion().empty() )
            l = wxSetlocaleTryUTF8(c, wxLocaleIdent(locId).Region(wxString()));
    }

    return l;
}

// ----------------------------------------------------------------------------
// wxUILocale implementation for Unix
// ----------------------------------------------------------------------------

wxUILocaleImplUnix::wxUILocaleImplUnix(wxLocaleIdent locId
#ifdef HAVE_LOCALE_T
                                      , locale_t loc
#endif // HAVE_LOCALE_T
                                      )
                  : m_locId(locId)
#ifdef HAVE_LOCALE_T
                  , m_locale(loc)
#endif // HAVE_LOCALE_T
{
}

wxUILocaleImplUnix::~wxUILocaleImplUnix()
{
#ifdef HAVE_LOCALE_T
    if ( m_locale )
        freelocale(m_locale);
#endif // HAVE_LOCALE_T
}

void
wxUILocaleImplUnix::Use()
{
    if ( m_locId.IsEmpty() )
    {
        // This is the default locale, it is already in use.
        return;
    }

    if ( !wxSetlocaleTryAll(LC_ALL, m_locId) )
    {
        // Some C libraries (namely glibc) still use old ISO 639,
        // so will translate the abbrev for them
        wxLocaleIdent locIdAlt(m_locId);

        const wxString& langOnly = m_locId.GetLanguage();
        if ( langOnly == wxS("he") )
            locIdAlt.Language(wxS("iw"));
        else if ( langOnly == wxS("id") )
            locIdAlt.Language(wxS("in"));
        else if ( langOnly == wxS("yi") )
            locIdAlt.Language(wxS("ji"));
        else if ( langOnly == wxS("nb") || langOnly == wxS("nn") )
        {
            locIdAlt.Language(wxS("no"));
            locIdAlt.Region(langOnly == wxS("nb") ? wxS("NO") : wxS("NY"));
        }
        else
        {
            // Nothing else to try.
            return;
        }

        wxSetlocaleTryAll(LC_ALL, locIdAlt);
    }
}

wxString
wxUILocaleImplUnix::GetName() const
{
    return m_locId.GetName();
}

#ifdef HAVE_LANGINFO_H

const char*
wxUILocaleImplUnix::GetLangInfo(nl_item item) const
{
#ifdef HAVE_LOCALE_T
    // We assume that we have nl_langinfo_l() if we have locale_t.
    if ( m_locale )
        return nl_langinfo_l(item, m_locale);
#endif // HAVE_LOCALE_T

    return nl_langinfo(item);
}

#endif // HAVE_LANGINFO_H

wxString
wxUILocaleImplUnix::GetInfo(wxLocaleInfo index, wxLocaleCategory cat) const
{
#ifdef HAVE_LANGINFO_H
    switch ( index )
    {
        case wxLOCALE_THOUSANDS_SEP:
#ifdef MON_THOUSANDS_SEP
            if ( cat == wxLOCALE_CAT_MONEY )
                return GetLangInfo(MON_THOUSANDS_SEP);
#endif
            return GetLangInfo(THOUSEP);

        case wxLOCALE_DECIMAL_POINT:
#ifdef MON_DECIMAL_POINT
            if ( cat == wxLOCALE_CAT_MONEY )
                return GetLangInfo(MON_DECIMAL_POINT);
#endif

            return GetLangInfo(RADIXCHAR);

        case wxLOCALE_SHORT_DATE_FMT:
            return GetLangInfo(D_FMT);

        case wxLOCALE_DATE_TIME_FMT:
            return GetLangInfo(D_T_FMT);

        case wxLOCALE_TIME_FMT:
            return GetLangInfo(T_FMT);

        case wxLOCALE_LONG_DATE_FMT:
            return wxGetDateFormatOnly(GetLangInfo(D_T_FMT));

        default:
            wxFAIL_MSG( "unknown wxLocaleInfo value" );
    }

    return wxString();
#else // !HAVE_LANGINFO_H
    // Currently we rely on the user code not calling setlocale() itself, so
    // that the current locale is still the same as was set in the ctor.
    //
    // If this assumption turns out to be wrong, we could use wxLocaleSetter to
    // temporarily change the locale here (maybe only if setlocale(NULL) result
    // differs from the expected one).
    return wxLocale::GetInfo(index, cat);
#endif // HAVE_LANGINFO_H/!HAVE_LANGINFO_H
}

int
wxUILocaleImplUnix::CompareStrings(const wxString& lhs, const wxString& rhs,
                                   int WXUNUSED(flags)) const
{
    int rc;

#ifdef HAVE_LOCALE_T
    if ( m_locale )
        rc = wcscoll_l(lhs.wc_str(), rhs.wc_str(), m_locale);
    else
#endif // HAVE_LOCALE_T
        rc = wcscoll(lhs.wc_str(), rhs.wc_str());

    if ( rc < 0 )
        return -1;

    if ( rc > 0 )
        return 1;

    return 0;
}

/* static */
wxUILocaleImpl* wxUILocaleImpl::CreateStdC()
{
    return new wxUILocaleImplUnix(wxLocaleIdent().Language("C"));
}

/* static */
wxUILocaleImpl* wxUILocaleImpl::CreateUserDefault()
{
    return new wxUILocaleImplUnix(wxLocaleIdent());
}

/* static */
wxUILocaleImpl* wxUILocaleImpl::CreateForLocale(const wxLocaleIdent& locIdOrig)
{
#ifdef HAVE_LOCALE_T
    // Make a copy of it because it can be modified below.
    wxLocaleIdent locId = locIdOrig;

    const locale_t loc = TryCreateMatchingLocale(locId);
    if ( !loc )
        return NULL;

    return new wxUILocaleImplUnix(locId, loc);
#else // !HAVE_LOCALE_T
    // We can't check locale availability without changing it in this case, so
    // just assume it's valid.
    return new wxUILocaleImplUnix(locIdOrig);
#endif // HAVE_LOCALE_T/!HAVE_LOCALE_T
}

#endif // wxUSE_INTL
